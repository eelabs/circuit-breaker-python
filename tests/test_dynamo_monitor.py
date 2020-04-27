from requests import PreparedRequest, Response
from requests_circuit_breaker.write_to_dynamo_monitor import WriteToDynamoMonitor
from requests_circuit_breaker.service_monitor_model import ServiceMonitor
import os


def test_write_trip_event_to_db():
    print("http://{0}:8000".format(os.getenv("DYNAMO_HOST")))
    ServiceMonitor.create_table(wait=True)
    monitor = WriteToDynamoMonitor()
    result = monitor.trip("some-service")
    assert result.id is not None
    fetched_result = ServiceMonitor.query(result.service_name, ServiceMonitor.id == result.id).next()
    assert fetched_result.id == result.id
    assert fetched_result.event_type == "TRIP"
    assert fetched_result.timestamp == result.timestamp
    assert fetched_result.ttl == result.ttl


def test_write_reset_event_to_db():
    ServiceMonitor.create_table(wait=True)
    monitor = WriteToDynamoMonitor()
    result = monitor.reset("some-service")
    assert result.id is not None
    fetched_result = ServiceMonitor.query(result.service_name, ServiceMonitor.id == result.id).next()
    assert fetched_result.id == result.id
    assert fetched_result.event_type == "RESET"
    assert fetched_result.timestamp == result.timestamp
    assert fetched_result.ttl == result.ttl


def test_write_failure_event_to_db():
    ServiceMonitor.create_table(wait=True)
    monitor = WriteToDynamoMonitor()
    request = PreparedRequest()
    request.body = "The body of request"
    request.headers = {"bill": "Some bill"}
    response = Response()
    response.status_code = 500
    response.headers['ben'] = "Some Ben"
    response.data = "The response text"
    result = monitor.failure("some-service", request, response, 1108)
    assert result.id is not None
    fetched_result = ServiceMonitor.query(result.service_name, ServiceMonitor.id == result.id).next()
    assert fetched_result.id == result.id
    assert fetched_result.event_type == "FAILED"
    assert fetched_result.timestamp == result.timestamp
    assert fetched_result.ttl == result.ttl
