"""# Hyper-parameters set according to OpenAI's site:
https://platform.openai.com/docs/guides/rate-limits

## OpenAI defines 5 rate limits type.
RPM: Rate per minute
TPM: Tokens per minute
RPD: Rate per day
TPD: Tokens per day
IPM: Image per minute (useless for us now)

## Rate limits (Tier 1 as example)
This is a high level summary and there are per-model exceptions to these limits
(e.g. some legacy models or models with larger context windows have different
rate limits). To view the exact rate limits per model for your account, visit
the limits section of your account settings.

MODEL	                RPM	    RPD	    TPM	        BATCH QUEUE LIMIT
gpt-4-turbo	            500	    -	    30,000	    90,000
gpt-4	                500	    10,000	10,000	    100,000
gpt-3.5-turbo	        3,500	10,000	60,000	    200,000
text-embedding-3-large	3,000	-	    1,000,000	3,000,000
text-embedding-3-small	3,000	-	    1,000,000	3,000,000
text-embedding-ada-002	3,000	-	    1,000,000	3,000,000

## Price:
https://openai.com/api/pricing/
|Model                  |Input                  |Output|
|-|-|-|
|gpt-4-turbo-2024-04-09 |US$10.00 / 1M tokens   |US$ 30.00 / 1M tokens|
|gpt-4                  |US$30.00 / 1M tokens   |US$ 60.00 / 1M tokens|
|gpt-4-32k              |US$60.00 / 1M tokens   |US$120.00 / 1M tokens|
|gpt-3.5-turbo-0125     |US$ 0.50 / 1M tokens   |US$  1.50 / 1M tokens|
|gpt-3.5-turbo-instruct |US$ 1.50 / 1M tokens   |US$  2.00 / 1M tokens|

NOTE: The rate limits are subject to change at any time.
This module provides a thread-safe singleton class `ClientPool` that
manages a pool of OpenAI API clients. It is designed to be used as a
context manager to ensure that clients are properly released back to the
pool when they are no longer in use.

The `ClientPool` class is a singleton, meaning that only one instance of it
can exist at any given time. This is achieved by using the `ThreadSafeSingleton`
metaclass, which ensures that only one instance of the class is created
regardless of the number of threads.

Example:
    get_from_pool = ClientPool([
        {"key": "YOUR_API_KEY_1", "url": "https://api.openai.com/v1"},
        {"key": "YOUR_API_KEY_2", "url": "https://api.openai.com/v1"},
        {"key": "YOUR_API_KEY_3", "url": "https://api.openai.com/v1"},
    ])

    with get_from_pool as client_args:
        client = OpenAI(**client_args)
        completion = client.chat.completions.create(**model_args)
        return completion.choices[0].message
"""

import random
import time
from abc import abstractmethod
from heapq import heapify, heappop, heappush
from typing import Dict, List, NewType, Optional

from loguru import logger
from openai import RateLimitError

from llms.exceptions import APIKeyPoolEmptyError

A_DAY_IN_SECONDS = 24 * 60 * 60
A_MINITE_IN_SECONDS = 60

RPM_INTERVAL = 500
TPM_QUOTA = 30_000

INPUT_PRICE_PER_TOKEN = 10
OUTPUT_PRICE_PER_TOKEN = 30

ClientArgs = NewType("ClientArgs", Dict[str, str | List[str]])


class Resource:
    def __init__(
        self,
        api_key: str,
        base_url: str,
        organization: Optional[str] = None,
        project: Optional[str] = None,
        max_retries: int = 2,
        timeout: Optional[float] = None,
    ) -> None:
        # # client args
        self.client_args: ClientArgs = {
            "api_key": api_key,
            "base_url": self._enforce_trailing_slash(base_url),
            "organization": organization,
            "project": project,
            "max_retries": max_retries,
            "timeout": timeout,
        }

        # priority items
        self._last_used_time: float = time.time()
        self._request_count: int = 0
        self._prompt_tokens: int = 0
        self._completion_tokens: int = 0
        self._total_tokens: int = 0
        # self._client = OpenAI(api_key=self.api_key, base_url=self.base_url)

    def __lt__(self, other: "Resource") -> bool:
        """Compare two resources based on request rate, token usage and price
        Args:
            other (Resource): The other resource to compare with
        Returns:
            bool: True if this resource has a lower request rate and token usage
            than the other resource, False otherwise
        """
        if abs(self._last_used_time - other._last_used_time) > A_MINITE_IN_SECONDS:
            return self._last_used_time < other._last_used_time
        elif abs(self._request_count - other._request_count) > RPM_INTERVAL:
            return self._request_count < other._request_count
        else:
            return (
                self._prompt_tokens * INPUT_PRICE_PER_TOKEN
                + self._completion_tokens * OUTPUT_PRICE_PER_TOKEN
            ) < (
                other._prompt_tokens * INPUT_PRICE_PER_TOKEN
                + other._completion_tokens * OUTPUT_PRICE_PER_TOKEN
            )

    def __gt__(self, other: "Resource") -> bool:
        """Compare two resources based on request rate and token usage
        Args:
            other (Resource): The other resource to compare with
        Returns:
            bool: True if this resource has a higher request rate and token usage
            than the other resource, False otherwise
        """
        return not self.__lt__(other)

    def _enforce_trailing_slash(self, url: str) -> str:
        if not url.endswith("/"):
            url += "/"
        return url

    def update(self, usage: Dict[str, int]) -> "Resource":
        current_time = time.time()
        assert self._last_used_time <= current_time
        assert (
            usage["prompt_tokens"] + usage["completion_tokens"] == usage["total_tokens"]
        )
        if current_time - self._last_used_time > A_MINITE_IN_SECONDS:
            self._request_count = 1
            self._prompt_tokens = usage["prompt_tokens"]
            self._completion_tokens = usage["completion_tokens"]
        else:
            self._request_count += 1
            self._prompt_tokens += usage["prompt_tokens"]
            self._completion_tokens += usage["completion_tokens"]

        return self


class Pool:
    def __init__(self, client_args: ClientArgs) -> None:
        assert "api_keys" in client_args or "api_key" in client_args
        assert not ("api_keys" in client_args and "api_key" in client_args)

        if "api_key" in client_args:
            self.queue: List[Resource] = [Resource(**client_args)]
        elif "api_keys" in client_args:
            self.queue: List[Resource] = [
                Resource(
                    api_key=api_key,
                    base_url=client_args["base_url"],
                    organization=client_args.get("organization", None),
                    project=client_args.get("project", None),
                    max_retries=client_args.get("max_retries", 2),
                    timeout=client_args.get("timeout", None),
                )
                for api_key in client_args["api_keys"]
            ]

        self._index: int = 0

    def __len__(self) -> int:
        return len(self.queue)

    @abstractmethod
    def __enter__(self, **kwargs) -> ClientArgs:
        """Get a client from the pool and return it as a context manager."""
        raise NotImplementedError

    @abstractmethod
    def __exit__(self, exc_type, exc_value, exc_traceback) -> bool:
        """Put the resource back in the pool."""
        raise NotImplementedError

    def _remove_cur_arg(self) -> None:
        logger.info(f"removing api key {self.queue[self._index]}")
        _ = self.client_args.pop(self._index)
        if len(self) == 0:
            raise APIKeyPoolEmptyError("api key pool is empty")


class PQPool(Pool):
    def __init__(self, client_args: ClientArgs) -> None:
        super().__init__(client_args)  # unlimited size

        # Initialize the heap with resources
        heapify(self.queue)

    def __enter__(self, **kwargs) -> ClientArgs:
        """Get a client from the pool and return it as a context manager."""

        if len(self) == 0:
            raise APIKeyPoolEmptyError("api key pool is empty")

        self._cur_resource = heappop(self.queue)

        return self._cur_resource.client_args

    def __exit__(self, exc_type, exc_value, exc_traceback) -> bool:
        """Put the resource back in the pool."""

        # TODO how to update the usage?
        self._cur_usage = {
            "prompt_tokens": 0,
            "completion_tokens": 0,
            "total_tokens": 0,
        }
        heappush(self.queue, self._cur_resource.update(self._cur_usage))
        if exc_type is not None:
            # Log the exception or handle it as needed
            logger.error(f"Client Pool Error: {exc_type}, {exc_value}")
            return False
        return True


class RandomPool(Pool):
    def __init__(self, client_args: ClientArgs) -> None:
        super().__init__(client_args)
        logger.info(f"initializing RandomPool with {len(client_args)} api keys")
        logger.info(f"client args: {client_args}")

    def __enter__(self, *args, **kwargs) -> ClientArgs:
        """Get a client from the pool and return it as a context manager."""

        if len(self) == 0:
            raise APIKeyPoolEmptyError("api key pool is empty")

        self._index = random.randint(0, len(self) - 1)
        return self.queue[self._index].client_args

    def __exit__(self, exc_type, exc_value, exc_traceback) -> bool:
        """Put the resource back in the pool."""

        if exc_value is not None:
            if (
                exc_type is RateLimitError
                and exc_value.status_code == 429
                and judge_quota_exceeded(exc_value.message)
            ):
                self._remove_cur_arg()
            return False
        return True


# class SpinPool(metaclass=Singleton):
class SpinPool(Pool):
    def __init__(self, client_args: ClientArgs) -> None:
        super().__init__(client_args)
        random.shuffle(self.queue)

    def __enter__(self, *arg, **kwargs) -> ClientArgs:
        """Get a client from the pool and return it as a context manager."""

        if len(self) == 0:
            raise APIKeyPoolEmptyError("api key pool is empty")

        return self.queue[self._index].client_args

    def __exit__(self, exc_type, exc_value, exc_traceback) -> bool:
        """Put the resource back in the pool."""

        if exc_value is None:
            self._index = (self._index + 1) % len(self)
            return True
        else:
            if (
                exc_type is RateLimitError
                and exc_value.status_code == 429
                and judge_quota_exceeded(exc_value.message)
            ):
                self._remove_cur_arg()
            else:
                self._index = (self._index + 1) % len(self)
            return False


def judge_quota_exceeded(message: str) -> bool:
    return any(word in message.lower() for word in ("quota", "bill", "额度", "余额"))
