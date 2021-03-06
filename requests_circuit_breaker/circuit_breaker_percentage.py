from requests.models import PreparedRequest, Response
import time
from requests_circuit_breaker.circuit_breaker import CircuitBreaker
from requests_circuit_breaker.monitoring import Monitor
from requests_circuit_breaker.storage import Storage
from typing import List


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

      >>> from requests_circuit_breaker.circuit_breaker_percentage import PercentageCircuitBreaker
      >>> from requests_circuit_breaker.storage import InMemoryStorage
      >>> breaker = PercentageCircuitBreaker("my-service", storage=InMemoryStorage())

    """
    def __init__(self, service: str, storage: Storage = None, monitors: List[Monitor] = None, ttl: int = 60,
                 percent_failed: int = 10, re_enable_after_seconds: int = 180, minimum_failures=5):
        super().__init__(service, "PercentCB", storage=storage, monitors=monitors if monitors else [], ttl=ttl,
                         percent_failed=percent_failed, re_enable_after_seconds=re_enable_after_seconds,
                         minimum_failures=minimum_failures)
        self.ttl = ttl
        self.percent_failed = percent_failed
        self.re_enable_after_seconds = re_enable_after_seconds
        self._last_open = 0
        self.minimum_events = minimum_failures

    @property
    def is_closed(self):
        interval = time.time() - self.re_enable_after_seconds
        if self._last_open >= interval:
            return False
        else:
            self._last_open = self.storage.last_open(self.service)
            return self._last_open < interval

    def register_success(self, request: PreparedRequest, response: Response, elapsed: int):
        super().register_success(request, response, elapsed)
        self.storage.register_event_returning_count("{0}-{1}".format(self.service, "count"), self.ttl)
        if self._last_open < time.time() - self.re_enable_after_seconds:
            self.storage.update_open(self.service, 0)
            self.reset()

    def register_error(self, request: PreparedRequest, response: Response, elapsed: int):
        super().register_error(request, response, elapsed)
        total = self.storage.register_event_returning_count("{0}-{1}".format(self.service, "count"), self.ttl)
        errors = self.storage.register_event_returning_count("{0}-{1}".format(self.service, "error"), self.ttl)
        if errors >= self.minimum_events and (100 / total * errors) >= self.percent_failed:
            self.storage.update_open(self.service, int(time.time()))
            self.trip()
