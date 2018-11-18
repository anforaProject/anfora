import logging
import coloredlogs

coloredlogs.install()

logging.basicConfig(
    level=logging.CRITICAL,
    format="[%(asctime)s] %(levelname)s: %(message)s",
    handlers=[logging.StreamHandler()]
)