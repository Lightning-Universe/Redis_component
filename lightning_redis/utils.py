import os

RUNNING_ON_CLOUD = bool(os.getenv("LIGHTNING_CLOUD_WORK_ID"))
