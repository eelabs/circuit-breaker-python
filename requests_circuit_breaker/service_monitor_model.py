import os
from pynamodb.models import Model
from pynamodb.attributes import (
    UnicodeAttribute, ListAttribute, NumberAttribute, MapAttribute
)

SERVICE_MONITOR_TABLE = os.environ['SERVICE_MONITOR_TABLE']
IS_OFFLINE = os.environ.get('IS_OFFLINE')


class HeaderAttribute(MapAttribute):
    key = UnicodeAttribute()
    value = UnicodeAttribute()


class OutboundRequest(MapAttribute):
    body = UnicodeAttribute()
    headers = ListAttribute(of=HeaderAttribute)


class InboundResponse(MapAttribute):
    body = UnicodeAttribute()
    headers = ListAttribute(of=HeaderAttribute)
    status = NumberAttribute()


class ServiceMonitor(Model):
    class Meta:
        table_name = SERVICE_MONITOR_TABLE
        region = 'eu-west-1'
        if IS_OFFLINE:
            host = "http://localhost:8000"
            write_capacity_units = 1
            read_capacity_units = 1
    service_name = UnicodeAttribute(hash_key=True)
    id = UnicodeAttribute(range_key=True)
    timestamp = NumberAttribute()
    event_type = UnicodeAttribute()
    request = OutboundRequest()
    response = InboundResponse()
    elapsed_time = NumberAttribute()
    ttl = NumberAttribute()
