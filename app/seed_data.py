from app.database import SessionLocal, engine, Base
from app.models import Product
from decimal import Decimal
from sqlalchemy import text
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    """Create all tables"""
    logger.info("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")

def seed_from_sql():
    """Execute the init-db.sql file"""
    sql_file = os.getenv('SEED_SQL_FILE', '/app/init-db.sql')

    if not os.path.exists(sql_file):
        logger.info(f"No SQL seed file found at {sql_file}")
        return

    try:
        # Read the SQL file
        with open(sql_file, 'r') as f:
            sql_content = f.read()

        # Execute SQL statements
        with engine.connect() as connection:
            # Start a transaction
            with connection.begin():
                statements = [s.strip() for s in sql_content.split(';') if s.strip()]
                for statement in statements:
                    logger.info(f"statement:{statement}")
                    if statement.upper().startswith('INSERT'):
                        try:
                            # Use text() to wrap raw SQL
                            connection.execute(text(statement))
                            logger.info(f"Executed: {statement[:80]}...")
                        except Exception as e:
                            # ON CONFLICT DO NOTHING will cause this
                            if "duplicate key" in str(e).lower():
                                logger.info("Data already exists, skipping...")
                            else:
                                logger.warning(f"Error executing statement: {e}")

            # Commit happens automatically with context manager
            logger.info("SQL seed file executed successfully")

    except Exception as e:
        logger.error(f"Error executing SQL seed file: {e}")
        raise

if __name__ == "__main__":
    init_db()
    seed_from_sql()
