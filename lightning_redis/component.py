import os
import random
import subprocess
import time
from pathlib import Path
from typing import List

from lightning.app import LightningWork
from lightning.app import BuildConfig

from lightning_redis.utils import RUNNING_ON_CLOUD

if RUNNING_ON_CLOUD:
    import redis


class CustomBuildConfig(BuildConfig):
    def __init__(self, build_commands: List[str], *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._build_commands = build_commands
        self.requirements = ["redis"]

    def build_commands(self) -> List[str]:
        return self._build_commands


class RedisComponent(LightningWork):
    def __init__(self):
        build_commands = (Path(__file__).parent / "build_commands.sh").read_text().splitlines()
        super().__init__(parallel=True, cloud_build_config=CustomBuildConfig(build_commands=build_commands))
        self._has_initialized = False
        rand_string = "".join([random.choice('abcdefghijklmnopqrstuvwxyz0123456789') for _ in range(20)])
        self.password = os.getenv('REDIS_PASSWORD', rand_string)

    def run(self):
        process = subprocess.Popen(['redis-server', '--port', str(self.port)])
        if not self._has_initialized:
            ret = redis.Redis(port=self.port).config_set('requirepass', 'mypassword')
            if ret:
                print("redis password set")
                self._has_initialized = True
        while True:
            try:
                redis.Redis(password=self.password, port=self.port).ping()
            except redis.exceptions.ConnectionError:
                print("redis is not up")
            exit_code = process.poll()
            if exit_code is not None:
                raise Exception(f'Redis exited with code {exit_code}')
            time.sleep(1)
