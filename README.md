# lightning_redis component

⚡ Redis Component for [Lightning](lightning.ai) ⚡


## To run lightning_redis

First, install lightning_redis:

```bash
lightning install component https://github.com/theUser/lightning_redis
```

Once the app is installed, use it in an app:

```python
from lightning_redis import RedisComponent
from lightning.app import LightningFlow, LightningApp
import redis


class LitApp(LightningFlow):
    def __init__(self) -> None:
        super().__init__()
        self.lightning_redis = RedisComponent()
        self.client = None

    def run(self):
        self.lightning_redis.run()
        if self.client is None:
            self.client = redis.Redis(
                host=self.lightning_redis.internal_ip,
                port=self.lightning_redis.port,
                password=self.lightning_redis.redis_password)


app = LightningApp(LitApp())
```

## Redis Password

By default, the RedisComponent will generate a 20 character password for you but if you wish to pass
a custom password for your redis, run your app with `--env REDIS_PASSWORD=<your password>`

For example:

```bash
lightning run app app.py --cloud --env REDIS_PASSWORD=<your password>
```
