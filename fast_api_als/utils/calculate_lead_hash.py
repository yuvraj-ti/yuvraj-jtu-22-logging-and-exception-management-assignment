import json
import logging
import copy
import hashlib

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)0.8s] %(message)s",
)
logger = logging.getLogger(__name__)


def calculate_lead_hash(obj):
    logger.info(f"calculating hash...")
    """MD5 hash of a dictionary."""
    adf = copy.deepcopy(obj)
    adf['adf']['prospect'].pop('provider')
    adf['adf']['prospect'].pop('requestdate')
    dhash = hashlib.md5()
    encoded = json.dumps(adf, sort_keys=True).encode()
    dhash.update(encoded)
    logger.info("hash calculated without provider data")
    return dhash.hexdigest()
