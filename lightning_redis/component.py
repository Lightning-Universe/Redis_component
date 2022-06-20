import os
import subprocess
import time
from typing import List

import redis
from lightning.app import BuildConfig, LightningWork

from lightning_redis.build_commands import build_commands
from lightning_redis.utils import RUNNING_AT_CLOUD, rand_password_gen

REDIS_STARTUP_BUFFER_SECONDS = 60


class CustomBuildConfig(BuildConfig):
    def __init__(self):
        super().__init__()
        self._build_commands = build_commands
        self.requirements = ["redis"]

    def build_commands(self) -> List[str]:
        return self._build_commands


class RedisComponent(LightningWork):
    def __init__(self):
        super().__init__(parallel=True, cloud_build_config=CustomBuildConfig())
        self._redis_process = None
        self.redis_password = None
        self.redis_host = None
        self.redis_port = None
        self.running = False

    def _init_redis(self, docker=False):
        if docker:
            self._redis_process = subprocess.Popen(
                ["docker", "run", "-it", "--rm", "-p", "6379:6379", "redis"]
            )
        else:
            self._redis_process = subprocess.Popen(
                ["redis-server", "--port", str(self.redis_port)]
            )
        ret = redis.Redis(port=self.redis_port).config_set(
            "requirepass", self.redis_password
        )
        if ret:
            print("redis password set")

    @staticmethod
    def _has_redis_installed():
        with open(os.devnull, "w") as devnull:
            try:
                proc = subprocess.Popen(
                    ["redis-server", "--version"], stdout=devnull, stderr=devnull
                )
            except FileNotFoundError:
                # redis server not installed
                return False
            else:
                status = proc.wait(timeout=5)
                proc.kill()
                return True if status == 0 else False

    @staticmethod
    def _has_docker_installed():
        with open(os.devnull, "w") as devnull:
            try:
                proc = subprocess.Popen(
                    ["docker", "stats", "--no-stream"], stdout=devnull, stderr=devnull
                )
            except FileNotFoundError:
                # docker server not installed or not running
                return False
            else:
                status = proc.wait(timeout=5)
                proc.kill()
                return True if status == 0 else False

    def on_exit(self):
        # it won't kill the child process forcefully
        self._redis_process.terminate()

    def run(self):
        # setup credentials
        self.redis_host = self.internal_ip if RUNNING_AT_CLOUD else "localhost"
        self.redis_port = self.port
        self.redis_password = os.getenv("REDIS_PASSWORD", rand_password_gen())

        # Setting up Redis - we either need the redis system
        # installation or a running docker service, so we can call redis docker image (only for local)
        if not RUNNING_AT_CLOUD:
            if self._has_redis_installed():
                self._init_redis(docker=False)
            elif self._has_docker_installed():
                self._init_redis(docker=True)
            else:
                raise RuntimeError(
                    "Cannot run redis locally. You need to have either redis-server "
                    "or docker installed in your machine. If docker is installed already, make sure"
                    "the service is running. This is not a problem if you are running the "
                    "app in cloud, as we will install the redis-server for you there"
                )
        else:
            self._init_redis(docker=False)

        while True:
            try:
                redis.Redis(password=self.redis_password, port=self.redis_port).ping()
                self.running = True
            except redis.exceptions.ConnectionError:
                self.running = False
                # below guard is to make sure we don't exit the redis before redis starts
                if time.perf_counter() > REDIS_STARTUP_BUFFER_SECONDS:
                    raise RuntimeError("Redis doesn't seem to be running. Exiting!!")
            time.sleep(1)
