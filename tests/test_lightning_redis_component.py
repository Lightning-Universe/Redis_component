r"""
To test a lightning component:

1. Init the component.
2. call .run()
"""
from unittest.mock import MagicMock

import pytest
import redis

import lightning_redis.component as component
from lightning_redis.component import RedisComponent


def test_redis_component(monkeypatch):
    subprocess_mock = MagicMock()
    process_mock = MagicMock()

    fake_port = 9090

    def popen(commands):
        assert commands == [
            "redis-server",
            "--port",
            str(fake_port),
            "--loadmodule",
            "/redismodules/redisearch.so",
        ]
        return process_mock

    # mocking Popen since we use that to run redis server command
    subprocess_mock.Popen = popen

    redis_mock = MagicMock()
    # this is a hack for the redis component to exit after the given count.
    redis_mock.check_count = 2

    def redis_class_init(password=None, port=None):
        if redis_mock.check_count <= 0:
            raise redis.exceptions.ConnectionError
        redis_mock.check_count -= 1
        if password:
            assert len(password) == 20
        assert port == fake_port
        return MagicMock()

    redis_mock.Redis = redis_class_init
    # since we mock the whole redis module
    redis_mock.exceptions.ConnectionError = redis.exceptions.ConnectionError
    monkeypatch.setattr(component, "subprocess", subprocess_mock)
    monkeypatch.setattr(component, "redis", redis_mock)
    monkeypatch.setattr(component, "RUNNING_AT_CLOUD", True)
    monkeypatch.setattr(component, "REDIS_STARTUP_BUFFER_SECONDS", 0)
    redis_component = RedisComponent()

    # setting the fake port we created before as the work port
    redis_component._port = fake_port

    # should exit with exception on 4th attempt as we set process_mock.poll_count = 3
    with pytest.raises(RuntimeError, match="Redis didn't start within 0 seconds"):
        redis_component.run()
