from requests_circuit_breaker import PercentageCircuitBreaker
from requests_circuit_breaker.storage import InMemoryStorage


def test_percentage_failed_should_not_trip_breaker_when_less_than_minimum_error_count_reached():
    breaker = PercentageCircuitBreaker("my_service", ttl=10, percent_failed=50, re_enable_after_seconds=60, storage=InMemoryStorage(), minimum_failures=3)
    assert breaker.is_closed is True
    breaker.register_error(None, None)
    breaker.register_error(None, None)
    breaker.register_success(None, None)
    breaker.register_success(None, None)
    assert breaker.is_closed is True

    breaker.register_error(None, None)
    assert breaker.is_closed is False

def test_percentage_failed_should_not_trip_breaker_when_minimum_events_exceeded_but_failures_below_threshold():
    breaker = PercentageCircuitBreaker("my_service", ttl=10, percent_failed=50, re_enable_after_seconds=60, storage=InMemoryStorage(), minimum_failures=2)

    breaker.register_error(None, None)
    breaker.register_error(None, None)
    breaker.register_success(None, None)
    breaker.register_success(None, None)
    breaker.register_success(None, None)
    assert breaker.is_closed is True


def test_tripped_breaker_does_not_reset_on_success_within_re_enable_time():
    breaker = PercentageCircuitBreaker("my_service", ttl=10, percent_failed=50, re_enable_after_seconds=60, storage=InMemoryStorage(), minimum_failures=2)

    breaker.register_error(None, None)
    breaker.register_error(None, None)
    breaker.register_error(None, None)
    assert breaker.is_closed is False
    breaker.register_success(None, None)
    assert breaker.is_closed is False
