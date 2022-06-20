r"""
To test a lightning component:

1. Init the component.
2. call .run()
"""
from unittest.mock import MagicMock

import pytest

from lightning_redis.component import RedisComponent
import lightning_redis.component as component


def test_redis_component(monkeypatch):
    subprocess_mock = MagicMock()
    process_mock = MagicMock()

    fake_port = 9090

    def popen(commands):
        assert commands == ['redis-server', '--port', str(fake_port)]
        return process_mock

    # mocking Popen since we use that to run redis server command
    subprocess_mock.Popen = popen

    # this is a hack for the redis component to exit after the given count. The poll
    # function is being called inside the `run` method of count and if that returns
    # non-empty status code, that means the redis server has exited and hence the
    # component will exit with an exception
    process_mock.poll_count = 2

    def poll(*args, **kwargs):
        if process_mock.poll_count <= 0:
            return 1
        process_mock.poll_count -= 1
        return None

    process_mock.poll = poll

    redis_mock = MagicMock()
    monkeypatch.setattr(component, "subprocess", subprocess_mock)
    monkeypatch.setattr(component, "redis", redis_mock)
    redis = RedisComponent()

    # setting the fake port we created before as the work port
    redis._port = fake_port

    # should exit with exception on 4th attempt as we set process_mock.poll_count = 3
    with pytest.raises(Exception, match="Redis exited with code"):
        redis.run()

    assert len(redis_mock.method_calls) == 4
    assert redis_mock.method_calls[0].kwargs == {'port': fake_port}
    for mock_call in redis_mock.method_calls[1:]:
        assert len(mock_call.kwargs["password"]) == 20
        assert mock_call.kwargs["port"] == fake_port


