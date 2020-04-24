from io import BytesIO
from dataclasses import dataclass
from typing import Union, Tuple, Text, Container, Optional, Mapping

from requests.adapters import HTTPAdapter
from requests.models import Response, PreparedRequest


class CircuitBreaker(object):

    def __init__(self, service: str):
        self.service = service

    @property
    def is_closed(self):
        return True

    def register_success(self, request: PreparedRequest, response: Response):
        pass

    def register_error(self, request: PreparedRequest, response: Response):
        pass


class CircuitBreakerAdapter(HTTPAdapter):
    """HTTP Adapter for requests

    Provides a circuit breaker for requests which prevents HTTP traffic being sent to the downstream service
    when the chosen :class: `CircuitBreaker <CircuitBreaker>` implementation trips.

    :param breaker: The circuit breaker to use

    Usage::

      >>> import requests
      >>> from breaker.storage import InMemoryStorage
      >>> from breaker.circuit_breaker_percentage import PercentageCircuitBreaker
      >>> from breaker.circuit_breaker import CircuitBreakerAdapter
      >>> breaker = PercentageCircuitBreaker("my-service", storage=InMemoryStorage())
      >>> adapter = CircuitBreakerAdapter(breaker)
      >>> session = requests.Session()
      >>> session.mount("http://getstatuscode.com", adapter)
      >>> session.get("http://getstatuscode.com/200")

    """
    def __init__(self, breaker: CircuitBreaker, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.breaker = breaker

    def send(self, request: PreparedRequest,
             stream: bool = ...,
             timeout: Union[None, float, Tuple[float, float], Tuple[float, None]] = ...,
             verify: Union[bool, str] = ...,
             cert: Union[None, Union[bytes, Text], Container[Union[bytes, Text]]] = ...,
             proxies: Optional[Mapping[str, str]] = ...) -> Response:
        if self.breaker.is_closed:
            response = super().send(request, stream, timeout, verify, cert, proxies)
            if response.status_code > 499:
                self.breaker.register_error(request, response)
            else:
                self.breaker.register_success(request, response)
            return response
        else:
            return self.build_response(request, DummyResponse(self.breaker.service))


@dataclass
class DummyResponse(object):
    service: str
    status: int = 500
    headers = {"X-Circuit-Breaker": "breaker tripped"}
    cookies = []
    reason = "Circuit breaker tripped"

    @property
    def read(self):
        if not hasattr(self, "_message"):
            message = '{"errors": [{"msg": "Circuit breaker ' + self.service + ' tripped"}]}'
            self._message = BytesIO(message.encode("utf-8")).read
        return self._message
