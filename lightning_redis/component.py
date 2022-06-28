import os
import subprocess
import time

import redis
from lightning.app import LightningWork
from lightning_app import BuildConfig

from lightning_redis.utils import RUNNING_AT_CLOUD, rand_password_gen

REDIS_STARTUP_BUFFER_SECONDS = 60
DOCKER_IMAGE = "ghcr.io/gridai/lightning-redis:v0.1"


class RedisComponent(LightningWork):
    def __init__(self):
        super().__init__(
            parallel=True, cloud_build_config=BuildConfig(image=DOCKER_IMAGE)
        )
        self._redis_process = None
        self.redis_password = None
        self.redis_host = None
        self.redis_port = None
        self.running = False

    def _init_redis(self, docker=False):
        if docker:
            self._redis_process = subprocess.Popen(
                [
                    "docker",
                    "run",
                    "-it",
                    "--rm",
                    "-p",
                    "6379:6379",
                    DOCKER_IMAGE,
                ]
            )
        else:
            self._redis_process = subprocess.Popen(
                [
                    "redis-server",
                    "--port",
                    str(self.redis_port),
                    "--loadmodule",
                    "/redismodules/redisearch.so",
                ]
            )
        process_start_time = time.perf_counter()
        while time.perf_counter() - process_start_time < REDIS_STARTUP_BUFFER_SECONDS:
            if self._redis_process.poll() is not None:
                raise RuntimeError("Redis process exited before it started")
            self.running = self._is_redis_running()
            if self.running:
                break
            time.sleep(1)
        else:
            if docker:
                raise RuntimeError(
                    f"Redis didn't start within the {REDIS_STARTUP_BUFFER_SECONDS}. "
                    f"Try downloading the docker image {DOCKER_IMAGE} manually"
                )
            else:
                raise RuntimeError(
                    f"Redis didn't start within {REDIS_STARTUP_BUFFER_SECONDS} seconds"
                )
        ret = redis.Redis(port=self.redis_port).config_set(
            "requirepass", self.redis_password
        )
        if ret:
            print("redis password set")

    def _is_redis_running(self, password=None):
        try:
            redis.Redis(password=password, port=self.redis_port).ping()
            return True
        except redis.exceptions.ConnectionError:
            return False
        except redis.exceptions.ResponseError as e:
            return False

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
            if self._has_docker_installed():
                self._init_redis(docker=True)
            else:
                raise RuntimeError(
                    "Cannot run redis locally. You need to have either docker installed in your "
                    "machine for running this component locally. If docker is installed already, make sure"
                    "the service is running. This is not a problem if you are running the "
                    "app in cloud, as we will handle the installation of required tools"
                )
        else:
            self._init_redis(docker=False)
        while True:
            self.running = self._is_redis_running(password=self.redis_password)
            if not self.running:
                raise RuntimeError("Redis is not running")
            time.sleep(1)
