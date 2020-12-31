import logging
import os
from pprint import pprint as print
import sys

from dotenv import load_dotenv
from errorhandler import ErrorHandler  # type: ignore

from client import get_project_data
from configuration import get_configuration
from export import export

def _configure_logging(log_level: str):

    logger = logging.getLogger(__name__)

    level = os.environ.get(log_level, "INFO")
    logging.basicConfig(
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        level=level,
    )
    error_tracker = ErrorHandler()

    return logger, error_tracker

def main():
    load_dotenv()
    config = get_configuration(sys.argv[1:])

    logger, error_tracker = _configure_logging(config.log_level)

    logger.info("Starting iNaturalist project data extractor.")
    logger.info(f"Configuration: {config}")

    project_data = get_project_data(config)
    export(config, project_data)

    logger.info("Finished with data extraction")

    if error_tracker.fired:
        print("There was a fatal error, please review the log details above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
