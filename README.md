<!---:lai-name: LightningRedis--->

<div align="center">
<img src="static/lightning-redis.png" width="250px">

⚡ Redis Component for [Lightning](https://lightning.ai) ⚡

______________________________________________________________________

![Tests](https://github.com/Lightning-AI/lightning-redis/actions/workflows/ci-testing.yml/badge.svg)

</div>

## About

Redis component will set up redis server along with chosen redis modules and provide the credentials to access it
from other components. Although, it will not expose any abstractions for you to
access the redis server, you can use any redis client using the credentials provided
by this component. The example given below is using the official [python redis client](https://github.com/Redis/redis-py)
which can be installed using `pip install redis`.

## Install

First, install the component:

```bash
lightning install component git+https://github.com/Lightning-AI/lightning-redis.git@main
```

## Use the Component

Once this component is installed, use it in a Lightning App:

```python
from lightning_redis import RedisComponent
from lightning.app import LightningApp, LightningFlow
import redis


class LitApp(LightningFlow):
    def __init__(self) -> None:
        super().__init__()
        self.lightning_redis = RedisComponent()

    def run(self):
        # this will set up redis
        self.lightning_redis.run()

        # check if redis is running or not
        if self.lightning_redis.running:

            # creating a python client using the credentials
            client = redis.Redis(
                host=self.lightning_redis.redis_host,
                port=self.lightning_redis.redis_port,
                password=self.lightning_redis.redis_password,
            )
            print("is redis up?, ", client.ping())


app = LightningApp(LitApp())
```

## Testing Locally

```python
pytest tests
```

## Redis Password

By default, the RedisComponent will generate a 20 character password for you but if you wish to pass
a custom password for your redis, run your lightning app with `--env REDIS_PASSWORD=<your password>`

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
- [ ] self-heal on error
