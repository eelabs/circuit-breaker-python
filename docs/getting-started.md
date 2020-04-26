---
id: getting-started
title: Getting Started
---

## Pre-requisites

This is a Python library that works with [requests](https://pypi.org/project/requests/) as an adapter. You
need to be familiar with `requests`. We will show you how to integrate your circuit breakers into `requests` in 
a way that does not interfere with normal usages.

If you are running on a fixed server, you don't need to spin up Redis and can just go with installing 
`requests-circuit-breaker` without any of the optional extras.

You also need to be running [Python 3.8](https://docs.python.org/3/whatsnew/3.8.html). This is supported by AWS 
Lambdas. The examples here cover how to deploy a python REST endpoint as a Lambda on AWS behind an API Gateway,
spin up a Redis backed ElastiCache service and set up an example monitoring web application. You will need an
AWS account to try this out. NOTE: Some of these services (e.g. ElastiCache) do not have a free tier so there will
be a cost to it. 

The deployment code uses the [Serverless](https://serverless.com) framework which needs NodeJS installed. See the
`Serverless` documentation for minimum version requirements.

## Installing

For the base case, using an in-memory circuit breaker store, run:

```shell script
$ pip install requests-circuit-breaker
```

For a Redis backed storage, you need to include the Redis extra requirements:

```shell script
$ pip install requests-circuit-breaker[Redis]
```

To include storing failures and monitoring information in DynamoDB, install with the options:

```shell script
$ pip install requests-circuit-breaker[Redis,Monitor]
```

## Setting up a circuit breaker

You can register multiple circuit breakers, one per base URL that you want to protect. 

```python
import requests
from requests_circuit_breaker import CircuitBreakerAdapter
from requests_circuit_breaker import PercentageCircuitBreaker
from requests_circuit_breaker.storage import InMemoryStorage

# Use the default settings
breaker = PercentageCircuitBreaker("my-service", storage=InMemoryStorage())
adapter = CircuitBreakerAdapter(breaker)
session = requests.Session()
session.mount("https://path.to.my/service", adapter)

session.get("https://path.to.my/service/v1/user/123")
```

When making calls to the service, you need to use `session` instead of calling `requests` directly.