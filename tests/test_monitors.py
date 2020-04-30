from requests import PreparedRequest, Response

from requests_circuit_breaker import CircuitBreaker
from requests_circuit_breaker.monitoring import Monitor
from requests_circuit_breaker.storage import Storage
from unittest import mock


def test_monitors_get_called_on_success():
    monitor1 = TestMonitor()
    monitor2 = TestMonitor()
    breaker = CircuitBreaker("my-service", "dummy-breaker", storage=Storage(), monitors=[monitor1, monitor2])
    req = mock.MagicMock()
    res = mock.MagicMock()
    breaker.register_success(req, res, 20)
    assert monitor1.success_count == 1
    assert monitor2.success_count == 1


def test_monitors_get_called_on_failure():
    monitor1 = TestMonitor()
    monitor2 = TestMonitor()
    breaker = CircuitBreaker("my-service", "dummy-breaker", storage=Storage(), monitors=[monitor1, monitor2])
    req = mock.MagicMock()
    res = mock.MagicMock()
    breaker.register_error(req, res, 10)
    assert monitor1.failure_count == 1
    assert monitor2.failure_count == 1


def test_monitors_get_called_on_trip():
    monitor1 = TestMonitor()
    monitor2 = TestMonitor()
    breaker = CircuitBreaker("my-service", "dummy-breaker", storage=Storage(), monitors=[monitor1, monitor2])
    breaker.trip()
    assert monitor1.trip_count == 1
    assert monitor2.trip_count == 1


def test_monitors_get_called_on_reset():
    monitor1 = TestMonitor()
    monitor2 = TestMonitor()
    breaker = CircuitBreaker("my-service", "dummy-breaker", storage=Storage(), monitors=[monitor1, monitor2])
    breaker.reset()
    assert monitor1.reset_count == 1
    assert monitor2.reset_count == 1


class TestMonitor(Monitor):
    def __init__(self):
        super().__init__()
        self.success_count = 0
        self.failure_count = 0
        self.trip_count = 0
        self.reset_count = 0

    def success(self, service: str, request: PreparedRequest, response: Response, elapsed: int):
        super().success(service, request, response, elapsed)
        self.success_count += 1

    def failure(self, service: str, request: PreparedRequest, response: Response, elapsed: int):
        super().failure(service, request, response, elapsed)
        self.failure_count += 1

    def trip(self, service: str):
        super().trip(service)
        self.trip_count += 1

    def reset(self, service: str):
        super().reset(service)
        self.reset_count += 1
