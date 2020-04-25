# Python requests Circuit Breaker

![Build and test](https://github.com/eelabs/circuit-breaker-python/workflows/Build%20and%20test/badge.svg)
[![codecov](https://codecov.io/gh/eelabs/circuit-breaker-python/branch/master/graph/badge.svg)](https://codecov.io/gh/eelabs/circuit-breaker-python)
[![Publish docs](https://github.com/eelabs/circuit-breaker-python/workflows/Publish%20docs/badge.svg)](https://eelabs.github.io/circuit-breaker-python)
---

A python implementation of the [circuit breaker pattern](https://martinfowler.com/bliki/CircuitBreaker.html)
based on the [ruby implementation](https://github.com/pedro/cb2) by Pedro Belo. 

This implementation works as an adapter for the [requests](https://pypi.org/project/requests/) library. 
Although a distributed circuit breaker is usually anti-pattern, this is being used for AWS Lambdas which 
therefore need a distributed mechanism. It uses Redis as the storage mechanism, though there is an in memory 
store available.

Using a circuit breaker for your lambdas when a backend is having problems both reduces the pressure on the
backend, giving it a chance to scale / recover and means the lambda can return instantly, reducing the cost
of waiting on IO that is likely to fail. By keeping track of successes and failures, you can configure the
breaker to trip when a minimum number of errors have occurred within a period of time. It then stays tripped
until an amount of time has elapsed, e.g

- Given events tracked for URL `https://example.com` over a period of 120 seconds
- When 5 or more errors have been returned
- And the overall failure percentage is 10% or more
- Then don't send any traffic for the next 300 seconds

## Usage

Configure the circuit breaker
```python
from requests_circuit_breaker.circuit_breaker_percentage import PercentageCircuitBreaker
from requests_circuit_breaker.storage import RedisStorage

breaker = PercentageCircuitBreaker("my-service", 
    ttl=120, 
    percent_failed=10, 
    re_enable_after_seconds=300, 
    storage=RedisStorage(),
    minimum_failures=5)

```

Then register it with `requests`
```python
import requests
from requests_circuit_breaker.circuit_breaker import CircuitBreakerAdapter

adapter = CircuitBreakerAdapter(breaker)
session = requests.Session()
session.mount("https://example.com", adapter)
session.get("https://example.com/some/url")
```

Now making calls using the session will automatically return a `500` status code along with a response
header `"X-Circuit-Breaker": "breaker tripped"` when the circuit breaker trips instead of calling any
URL under `https://example.com`.

Multiple circuit breakers can be registered for different services under different URLs. Each circuit breaker
can re-use the same storage instance.