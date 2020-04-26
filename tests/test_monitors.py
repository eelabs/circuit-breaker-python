from requests import PreparedRequest, Response

from requests_circuit_breaker import CircuitBreaker
from requests_circuit_breaker.monitoring import Monitor
from requests_circuit_breaker.storage import Storage
from unittest import mock


def test_monitors_get_called_on_success():
    monitor1 = TestMonitor()
    monitor2 = TestMonitor()
    breaker = CircuitBreaker("my-service", storage=Storage(), monitors=[monitor1, monitor2])
    req = mock.MagicMock()
    res = mock.MagicMock()
    breaker.register_success(req, res)
    assert monitor1.success_count == 1
    assert monitor2.success_count == 1


def test_monitors_get_called_on_failure():
    monitor1 = TestMonitor()
    monitor2 = TestMonitor()
    breaker = CircuitBreaker("my-service", storage=Storage(), monitors=[monitor1, monitor2])
    req = mock.MagicMock()
    res = mock.MagicMock()
    breaker.register_error(req, res)
    assert monitor1.failure_count == 1
    assert monitor2.failure_count == 1


def test_monitors_get_called_on_trip():
    monitor1 = TestMonitor()
    monitor2 = TestMonitor()
    breaker = CircuitBreaker("my-service", storage=Storage(), monitors=[monitor1, monitor2])
    breaker.trip()
    assert monitor1.trip_count == 1
    assert monitor2.trip_count == 1


def test_monitors_get_called_on_reset():
    monitor1 = TestMonitor()
    monitor2 = TestMonitor()
    breaker = CircuitBreaker("my-service", storage=Storage(), monitors=[monitor1, monitor2])
    breaker.trip()
    assert monitor1.trip_count == 1
    assert monitor2.trip_count == 1


class TestMonitor(Monitor):
    def __init__(self):
        super().__init__()
        self.success_count = 0
        self.failure_count = 0
        self.trip_count = 0
        self.reset_count = 0

    def success(self, service: str, request: PreparedRequest, response: Response):
        super().success(service, request, response)
        self.success_count += 1

    def failure(self, service: str, request: PreparedRequest, response: Response):
        super().failure(service, request, response)
        self.failure_count += 1

    def trip(self, service: str):
        super().trip(service)
        self.trip_count += 1

    def reset(self, service: str):
        super().reset(service)
        self.reset_count += 1
