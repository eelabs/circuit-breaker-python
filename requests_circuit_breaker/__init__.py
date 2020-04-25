"""
A circuit breaker implementation that works as a requests adapter
"""
from requests_circuit_breaker.circuit_breaker import CircuitBreakerAdapter, CircuitBreaker
from requests_circuit_breaker.circuit_breaker_percentage import PercentageCircuitBreaker

VERSION = __version__ = '0.1.0'
__author__ = 'Chris Tarttelin and Equal Experts LTD'
__email__ = 'ctarttelin@equalexperts.com'
__url__ = 'https://eelabs.github.io/circuit-breaker'

__all__ = ['CircuitBreaker', 'CircuitBreakerAdapter', 'PercentageCircuitBreaker']
