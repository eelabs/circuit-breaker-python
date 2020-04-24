from requests.models import PreparedRequest, Response
import time
from breaker.circuit_breaker import CircuitBreaker
from breaker.storage import Storage


class PercentageCircuitBreaker(CircuitBreaker):
    """Circuit Breaker strategy :class:`PercentageCircuitBreaker <PercentageCircuitBreaker>` object,
    used as an input to :class: `CircuitBreakerAdapter <CircuitBreakerAdapter>`.

    Records the successful and failed requests and determines when to 'Trip the circuit', preventing
    further requests

    :param service: The name of the service being protected
    :param ttl: The amount of time to track events for in seconds. Older events are ignored
    :param percent_failed: The percentage of errors at which point the circuit breaker should trip
    :param re_enable_after_seconds: Once the circuit breaker trips, the length of time to wait before closing it again
    :param storage: Where to store the events
    :param minimum_failures: To prevent trips during low volumes, only trip after a minimum number of failures occurs

    Usage::

      >>> from breaker.circuit_breaker_percentage import PercentageCircuitBreaker
      >>> from breaker.storage import InMemoryStorage as Storage
      >>> breaker = PercentageCircuitBreaker("my-service", storage=InMemoryStorage())

    """
    def __init__(self, service: str, ttl: int = 60, percent_failed: int = 10, re_enable_after_seconds: int = 180,
                 storage: Storage = None, minimum_failures=5):
        super().__init__(service)
        self.ttl = ttl
        self.percent_failed = percent_failed
        self.re_enable_after_seconds = re_enable_after_seconds
        self.storage = storage
        self._last_open = 0
        self.minimum_events = minimum_failures
        storage.service_name = self.service
        storage.ttl = ttl

    @property
    def is_closed(self):
        interval = time.time() - self.re_enable_after_seconds
        if self._last_open >= interval:
            return False
        else:
            self._last_open = self.storage.last_open(self.service)
            return self._last_open < interval

    def register_success(self, request: PreparedRequest, response: Response):
        self.storage.register_event_returning_count("{0}-{1}".format(self.service, "count"), self.ttl)
        if self._last_open < time.time() - self.re_enable_after_seconds:
            self.storage.update_open(self.service, 0)

    def register_error(self, request: PreparedRequest, response: Response):
        total = self.storage.register_event_returning_count("{0}-{1}".format(self.service, "count"), self.ttl)
        errors = self.storage.register_event_returning_count("{0}-{1}".format(self.service, "error"), self.ttl)
        if errors >= self.minimum_events and (100 / total * errors) >= self.percent_failed:
            self.storage.update_open(self.service, int(time.time()))
