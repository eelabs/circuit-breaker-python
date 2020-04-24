from requests.models import PreparedRequest, Response

from breaker.circuit_breaker import CircuitBreaker, CircuitBreakerAdapter
import requests
from urllib3_mock import Responses


responses = Responses('requests.packages.urllib3')


@responses.activate
def test_successful_request_with_closed_circuit():
    breaker = StubCircuitBreaker("Some_service")
    s = requests.Session()
    a = CircuitBreakerAdapter(breaker)
    s.mount('http://getstatuscode.com', a)
    responses.add('GET', "/200", body='{"error": "boom"}', status=200, content_type="application/json")

    res = s.get("http://getstatuscode.com/200", headers={
        "Accept": "text/html",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X)"
    })
    assert res.status_code == 200
    assert breaker._error_count == 0
    assert breaker._success_count == 1


@responses.activate
def test_server_error_request_with_closed_circuit():
    breaker = StubCircuitBreaker("Some_service")
    s = requests.Session()
    a = CircuitBreakerAdapter(breaker)
    s.mount('http://getstatuscode.com', a)
    responses.add('GET', "/200", body='{"error": "boom"}', status=500, content_type="application/json")

    res = s.get("http://getstatuscode.com/200", headers={
        "Accept": "text/html",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X)"
    })
    assert res.status_code == 500
    assert breaker._error_count == 1


@responses.activate
def test_server_request_with_open_circuit():
    breaker = StubCircuitBreaker("Some_service", circuit_closed=False)
    s = requests.Session()
    a = CircuitBreakerAdapter(breaker)
    s.mount('http://getstatuscode.com', a)
    responses.add('GET', "/200", body='{"error": "boom"}', status=500, content_type="application/json")

    res = s.get("http://getstatuscode.com/200", headers={
        "Accept": "text/html",
        "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 13_2_3 like Mac OS X)"
    })

    assert res.status_code == 500
    assert breaker._error_count == 0
    assert breaker._success_count == 0
    assert len(responses.calls) == 0


class StubCircuitBreaker(CircuitBreaker):

    def __init__(self, service_name: str, circuit_closed=True):
        super().__init__(service_name)
        self._error_count = 0
        self._success_count = 0
        self._circuit_closed = circuit_closed

    @property
    def is_closed(self):
        return self._circuit_closed

    def register_error(self, request: PreparedRequest, response: Response):
        self._error_count += 1

    def register_success(self, request: PreparedRequest, response: Response):
        self._success_count += 1
