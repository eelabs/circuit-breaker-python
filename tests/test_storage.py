from requests_circuit_breaker.storage import InMemoryStorage, RedisStorage
import time
import pytest
from unittest import mock
import uuid


@pytest.mark.parametrize("storage", [InMemoryStorage(), RedisStorage()])
def test_count_of_events_removes_expired_events(storage):
    key = str(uuid.uuid4())
    ttl = 10
    set_historic_event(storage, key, ttl)
    storage.register_event_returning_count(key, ttl)
    count = storage.register_event_returning_count(key, ttl)
    assert count == 2


@pytest.mark.parametrize("storage", [InMemoryStorage(), RedisStorage()])
def test_last_open_is_retained(storage):
    service = "some_service"
    trip_time = int(time.time())
    storage.update_open(service, trip_time)
    assert storage.last_open(service) == trip_time


@pytest.mark.parametrize("storage", [InMemoryStorage(), RedisStorage()])
def test_last_open_initializes_to_zero(storage):
    service = str(uuid.uuid4())
    assert storage.last_open(service) == 0


@pytest.mark.parametrize("storage", [InMemoryStorage(), RedisStorage()])
def test_set_of_services_maintained_dynamically(storage):
    service = str(uuid.uuid4())
    storage.register_breaker(service, "BreakerType", config="Value")
    assert service in storage.registered_services


@mock.patch('time.time', mock.MagicMock(return_value=12345))
def set_historic_event(storage, key, ttl):
    count = storage.register_event_returning_count(key, ttl)
    assert count == 1
    return int(time.time())
