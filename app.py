from lightning_redis import RedisComponent
from lightning.app import LightningApp, LightningFlow
import redis


class LitApp(LightningFlow):
    def __init__(self) -> None:
        super().__init__()
        self.lightning_redis = RedisComponent()

    def run(self):
        self.lightning_redis.run()
        print("is redis up?, ", redis.Redis(
            host=self.lightning_redis.internal_ip,
            port=self.lightning_redis.port,
            password=self.lightning_redis.password).ping()
        )


app = LightningApp(LitApp())
