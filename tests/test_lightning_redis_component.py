r"""
To test a lightning component:

1. Init the component.
2. call .run()
"""
import os
# need to set this before importing anything so we can mimic running on cloud
os.environ["LIGHTNING_CLOUD_WORK_ID"] = "1"

from unittest.mock import MagicMock

from lightning_redis.component import RedisComponent
import lightning_redis.component as component


def test_redis_component(monkeypatch):
    subprocess_mock = MagicMock()
    popen_mock = MagicMock()
    subprocess_mock.Popen = lambda: popen_mock
    popen_mock.poll = MagicMock()

    redis_mock = MagicMock()
    monkeypatch.setattr(component, "subprocess", subprocess_mock)
    monkeypatch.setattr(component, "redis", redis_mock)
    redis = RedisComponent()
    redis.run()
    assert popen_mock.assert_called_once_with(['redis-server', '--port', redis.port])
