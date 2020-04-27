from requests import PreparedRequest, Response
from requests_circuit_breaker.monitoring import Monitor
from requests_circuit_breaker.service_monitor_model import ServiceMonitor, OutboundRequest, InboundResponse, HeaderAttribute
import uuid
import time
import os

MONITOR_TTL = os.getenv('MONITOR_TTL', 60*60*24*7)


class WriteToDynamoMonitor(Monitor):

    def success(self, service: str, request: PreparedRequest, response: Response, elapsed: int):
        # ignore successes
        pass

    def failure(self, service: str, request: PreparedRequest, response: Response, elapsed: int):
        request_headers = [HeaderAttribute(key=key, value=value) for key, value in request.headers.items()]
        outbound = OutboundRequest(body=request.body, headers=request_headers)
        response_headers = [HeaderAttribute(key=key, value=value) for key, value in response.headers.items()]
        inbound = InboundResponse(body=response.text, status=response.status_code, headers=response_headers)
        entry = ServiceMonitor(service,
                               str(uuid.uuid4()),
                               timestamp=int(time.time()),
                               event_type="FAILED",
                               request=outbound,
                               response=inbound,
                               elapsed_time=elapsed,
                               ttl=int(time.time())+MONITOR_TTL)
        entry.save()
        return entry

    def trip(self, service: str):
        entry = ServiceMonitor(service,
                               str(uuid.uuid4()),
                               timestamp=int(time.time()),
                               event_type="TRIP",
                               ttl=int(time.time())+MONITOR_TTL)
        entry.save()
        return entry

    def reset(self, service: str):
        entry = ServiceMonitor(service,
                               str(uuid.uuid4()),
                               timestamp=int(time.time()),
                               event_type="RESET",
                               ttl=int(time.time())+MONITOR_TTL)
        entry.save()
        return entry
