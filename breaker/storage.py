import time
from collections import defaultdict
import os
import redis
import uuid


class Storage:

    def last_open(self, service_name: str) -> int :
        pass

    def update_open(self, service_name: str, time_in_seconds: int):
        pass

    def register_event_returning_count(self, key: str, ttl: int) -> int :
        pass

    @property
    def registered_services(self) -> int:
        pass


class InMemoryStorage(Storage):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.service_events = defaultdict(list)
        self._last_open = defaultdict(int)
        self._services = set()

    def last_open(self, service_name):
        self._services.add(service_name)
        return self._last_open[service_name]

    def update_open(self, service_name: str, time_in_seconds: int):
        if time_in_seconds:
            self._last_open[service_name] = time_in_seconds
        elif service_name in self._last_open:
            del(self._last_open[service_name])

    def register_event_returning_count(self, key, ttl: int):
        entries = self.service_events[key]
        now = int(time.time())
        entries.append(now)
        filtered_entries = [entry for entry in entries if entry >= now - ttl]
        self.service_events[key] = filtered_entries
        return len(filtered_entries)

    @property
    def registered_services(self):
        return self._services


class RedisStorage(Storage):
    ALL_BREAKERS = "all_breakers"

    def __init__(self):
        super().__init__()
        self._client = redis.Redis(host=os.getenv('REDIS_HOST', 'localhost'))
        self._last_open = None

    def last_open(self, service_name) -> int:
        result = self._client.get(service_name)
        if result is None:
            self._client.set(service_name, 0)
            self._client.sadd(self.ALL_BREAKERS, service_name)
            return 0
        else:
            return int(str(result, "utf-8"))

    def update_open(self, service_name: str, time_in_seconds: int):
        if time_in_seconds is None or time_in_seconds == 0:
            self._client.set(service_name, 0)
        else:
            self._client.set(service_name, time_in_seconds)

    def register_event_returning_count(self, key: str, ttl: int):
        t = time.time()
        p = self._client.pipeline()
        p.zremrangebyscore(key, "-inf", int(t) - ttl)
        p.zadd(key, {uuid.uuid4().bytes: t})
        p.zcard(key)
        result = p.execute()
        return result.pop()

    @property
    def registered_services(self):
        return set([str(breaker, "utf-8") for breaker in self._client.smembers(self.ALL_BREAKERS)])
