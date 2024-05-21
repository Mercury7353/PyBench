# ADC LLMs Exceptions
class LLMError(Exception):
    """Base exception class for my_package errors."""

    ...


class FunctionCallDeprecationError(LLMError):
    """Raised when OpenaiAPI returns a message including 'function_call' field."""

    ...


class APIKeyPoolEmptyError(Exception):
    """Raised when client pool is empty."""

    ...
