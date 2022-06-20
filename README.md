# lightning-redis

⚡ Redis Component for [Lightning](lightning.ai) ⚡

## To run lightning_redis

First, install lightning_redis:

```bash
lightning install component https://github.com/theUser/lightning_redis
```

Once the app is installed, use it in an app:

```python
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
            print(
                "is redis up?, ",
                redis.Redis(
                    host=self.lightning_redis.redis_host,
                    port=self.lightning_redis.redis_port,
                    password=self.lightning_redis.redis_password,
                ).ping(),
            )


app = LightningApp(LitApp())
```

## Redis Password

By default, the RedisComponent will generate a 20 character password for you but if you wish to pass
a custom password for your redis, run your app with `--env REDIS_PASSWORD=<your password>`

For example:

```bash
lightning run app app.py --cloud --env REDIS_PASSWORD=<your password>
```

## Local Vs Cloud

In local, to avoid messing up the system, we don't install anything onto user's machine. Hence, user's either need to
install [redis-server](https://redis.io/docs/getting-started/installation/) or
[docker](https://docs.docker.com/engine/install/). Note that if redis-server is not installed and docker is installed,
we'll pull the latest `redis` image from docker hub and run it with `docker run`.
In cloud, none of this matters, as we will install the redis server as part of the initial setup

## Roadmap / TODO

- [ ] Test and verify windows support. It's not currently tested on Windows but it might work out of the box
- [ ] Redis module (if not all, at-least redis stack)
- [ ] DB backup and restore (both RDB and AOF) is not supported
