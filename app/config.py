import os
from dotenv import load_dotenv
import logging

load_dotenv()
logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://inventory_user:inventory_pass@localhost:5432/inventory_db"
)

# For debugging
logger.debug(f"Using database URL: {DATABASE_URL.replace('://inventory_user:inventory_pass@', '://****:****@')}")
