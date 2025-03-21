import logging
import traceback
from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.exc import OperationalError, ArgumentError
from google.cloud import bigquery
from google.auth.exceptions import GoogleAuthError
from google.api_core.exceptions import GoogleAPIError,Forbidden

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

def check_path(path):
    path_obj = Path(path)
    if not path_obj.exists():
        raise FileNotFoundError(f"Error: The path '{path}' does not exist.")


def validate_db_connection(db_uri):
    try:
        # Create engine but don't establish connection yet
        engine = create_engine(db_uri, connect_args={"connect_timeout": 5})  # 5 sec timeout

        # Establish connection
        with engine.connect() as connection:
            logger.info(f"Connection to database succesful!")

    except ArgumentError:
        raise ValueError(f"Invalid database URI")

    except OperationalError as e:
        raise ConnectionError(f"Database connection failed: {e}")

    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}")


def validate_bigquery_connection(project_id):
    try:
        # Create a BigQuery client
        client = bigquery.Client(project=project_id)

        # Attempt a simple query to check connectivity
        client.query("SELECT 1").result()
        logger.info(f"Success: Connected to Google BigQuery project")

    except GoogleAuthError:
        raise PermissionError("Authentication failed. Check your Google Cloud credentials.")

    except GoogleAPIError as e:
        raise ConnectionError(f"Failed to connect to BigQuery: {e}")

    except Exception as e:
        raise RuntimeError(f"Unexpected error: {e}")
