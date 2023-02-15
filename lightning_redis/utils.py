import os
import random

RUNNING_AT_CLOUD = (
    os.getenv("LIGHTNING_NODE_IP")
    and os.getenv("LIGHTNING_CLOUD_PROJECT_ID")
    and os.getenv("LIGHTNING_CLOUD_APP_ID")
    and os.getenv("LIGHTNING_CLOUD_WORK_ID")
)


def rand_password_gen(length=20):
    return "".join([random.choice("abcdefghijklmnopqrstuvwxyz0123456789") for _ in range(length)])
