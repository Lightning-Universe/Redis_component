from lightning_redis import RedisComponent
from lightning.app import LightningApp, LightningFlow
import redis


class LitApp(LightningFlow):
    def __init__(self) -> None:
        super().__init__()
        self.lightning_redis = RedisComponent()

    def run(self):
        self.lightning_redis.run()
        if self.lightning_redis.running:
            print("is redis up?, ", redis.Redis(
                host=self.lightning_redis.redis_host,
                port=self.lightning_redis.redis_port,
                password=self.lightning_redis.redis_password).ping()
            )


app = LightningApp(LitApp())
