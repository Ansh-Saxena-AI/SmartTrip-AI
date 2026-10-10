import asyncio
import json
from unittest.mock import MagicMock, patch

import src.clients.cache as cache


def setup_function():
    cache.reset_client()


def test_build_key_is_deterministic():
    key1 = cache.build_key("weather", (("Delhi",),), {"units": "metric"})
    key2 = cache.build_key("weather", (("Delhi",),), {"units": "metric"})

    assert key1 == key2


def test_cache_hit_skips_function():
    fake_redis = MagicMock()
    fake_redis.get.return_value = json.dumps({"temperature": 30})

    with patch.object(cache, "get_client", return_value=fake_redis):
        with patch.object(cache, "_read", return_value=(True, {"temperature": 30})):
            @cache.cached("weather", ttl=60)
            def get_weather(city):
                raise AssertionError("Function should not run on cache hit")

            assert get_weather("Delhi") == {"temperature": 30}


def test_cache_miss_runs_function_and_writes_result():
    with patch.object(cache, "_read", return_value=(False, None)):
        with patch.object(cache, "_write", side_effect=lambda key, value, ttl: value) as write:
            @cache.cached("weather", ttl=60)
            def get_weather(city):
                return {"city": city}

            assert get_weather("Delhi") == {"city": "Delhi"}
            write.assert_called_once()


def test_redis_unavailable_still_runs_function():
    with patch.object(cache, "_read", return_value=(False, None)):
        with patch.object(cache, "_write", side_effect=lambda key, value, ttl: value):
            @cache.cached("weather", ttl=60)
            def get_weather(city):
                return {"city": city}

            assert get_weather("Delhi") == {"city": "Delhi"}


def test_async_cache_miss_runs_function():
    with patch.object(cache, "_read", return_value=(False, None)):
        with patch.object(cache, "_write", side_effect=lambda key, value, ttl: value):
            @cache.async_cached("weather", ttl=60)
            async def get_weather(city):
                return {"city": city}

            result = asyncio.run(get_weather("Delhi"))
            assert result == {"city": "Delhi"}


def test_async_cache_hit_skips_function():
    with patch.object(cache, "_read", return_value=(True, {"city": "Delhi"})):
        @cache.async_cached("weather", ttl=60)
        async def get_weather(city):
            raise AssertionError("Function should not run on cache hit")

        result = asyncio.run(get_weather("Delhi"))
        assert result == {"city": "Delhi"}

def test_get_client_handles_connection_failure():
    cache.reset_client()

    with patch.object(cache, "CACHE_ENABLED", True):
        with patch.object(cache, "REDIS_URL", "redis://localhost:6379/0"):
            with patch.object(
                cache.redis.Redis,
                "from_url",
                side_effect=cache.redis.ConnectionError("Redis unavailable"),
            ):
                assert cache.get_client() is None

def test_decorated_function_runs_when_redis_connection_fails():
    cache.reset_client()

    with patch.object(cache, "CACHE_ENABLED", True):
        with patch.object(cache, "REDIS_URL", "redis://localhost:6379/0"):
            with patch.object(
                cache.redis.Redis,
                "from_url",
                side_effect=cache.redis.ConnectionError("Redis unavailable"),
            ):
                @cache.cached("weather", ttl=60)
                def get_weather(city):
                    return {"city": city}

                assert get_weather("Delhi") == {"city": "Delhi"}
