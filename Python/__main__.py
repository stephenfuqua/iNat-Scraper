import logging
from pprint import pprint as print
import sys

from dotenv import load_dotenv
from errorhandler import ErrorHandler  # type: ignore

from client import get_project_data
from configuration import get_configuration
from export import export, build_file_path

def _configure_logging(log_level: str):

    logger = logging.getLogger(__name__)

    logging.basicConfig(
        handlers=[
            logging.StreamHandler(sys.stdout),
        ],
        format="%(asctime)s - %(levelname)s - %(name)s - %(message)s",
        level=log_level,
    )
    error_tracker = ErrorHandler()

    return logger, error_tracker

def main():
    load_dotenv()
    config = get_configuration(sys.argv[1:])

    logger, error_tracker = _configure_logging(config.log_level)

    logger.info("Starting iNaturalist project data extractor.")
    logger.info(f"Configuration: {config}")

    file_path = build_file_path(config)

    while 1==1:
        project_data = get_project_data(config)

        if len(project_data) == 0:
            # This occurs when there are no more results "above" the last id.
            break

        export(file_path, project_data)

        config.last_id = project_data[-1]["id"]

    logger.info("Finished with data extraction")

    if error_tracker.fired:
        print("There was an error, please carefully review the log details above.")
        sys.exit(1)


if __name__ == "__main__":
    main()
