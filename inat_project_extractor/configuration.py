from dataclasses import dataclass
import os
from datetime import datetime
from typing import List

from configargparse import ArgParser # type: ignore

@dataclass
class Configuration:
    """
    Container for holding arguments / environment variables that control program
    operation.

    Parameters
    ----------
    api_token: str
        An API token acquired from https://www.inaturalist.org/users/api_token
    log_level: str
        Standard Python logging level, e.g. ERROR, WARNING, INFO, DEBUG
    user_name: str
        iNaturalist user name
    project_slug: str
        Slug (short name) of the project to extract
    page_size: int
        Number of records to retrieve per request. Default: 200. Max: 200. Use
        lower value for testing.
    output_file: str
        Directory path and name for output file.
    last_id: str
        The last observation ID from a previous download, used to start a fresh
        download from the next available observation.
    input_file: str
        An input file to merge with the downloaded data.
    """

    api_token: str
    log_level: str
    user_name: str
    project_slug: str
    page_size: int
    output_directory: str
    last_id: str
    input_file: str

    def _create_dir(self, output_type: str) -> str:
        dir = os.path.join(self.output_directory, output_type)
        if not os.path.exists(dir):
            os.mkdir(dir)

        return dir

    def _build_output_file_name(self, output_type_directory: str) -> str:
        timestamp = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")
        return os.path.join(output_type_directory, f"{self.project_slug}.{timestamp}.csv")

    def _delete_existing_file(self, file_path: str) -> str:
        if os.path.exists(file_path):
            os.remove(file_path)

    def _prep_file_path(self, output_type: str) -> str:
        output_type_directory = self._create_dir(output_type)
        file_path = self._build_output_file_name(output_type_directory)

        self._delete_existing_file(file_path)

        return file_path


    def get_api_file_output_path(self) -> str:
        """
        Builds the file path for the export process. If there is an existing output
        file with the same name then it will be deleted. Because of the timestamp
        in the name this should not occur.

        Parameters
        ----------
        config: Configuration
            A custom Configuration object containing important settings
        """
        return self._prep_file_path("api")

    def get_merge_file_output_path(self) -> str:
        """
        Builds the file path for the merged file. If there is an existing output
        file with the same name then it will be deleted. Because of the timestamp
        in the name this should not occur.

        Parameters
        ----------
        config: Configuration
            A custom Configuration object containing important settings
        """
        return self._prep_file_path("merged")


def get_configuration(args_in: List[str]) -> Configuration:
    """
    Retrieves configuration from the command line or environment variables.

    Parameters
    ----------
    args_in: List[str]
        The system arguments received by the main script

    Returns
    -------
    An object of type Configuration
    """

    parser = ArgParser()
    parser.add(
        "-t",
        "--api-token",
        required=True,
        help="An API token acquired from https://www.inaturalist.org/users/api_token",
        type=str,
        env_var="INAT_API_TOKEN"
    )
    parser.add(
        "-z",
        "--log-level",
        default="INFO",
        help="Standard Python logging level, e.g. ERROR, WARNING, INFO, DEBUG",
        type=str,
        env_var="LOG_LEVEL"
    )
    parser.add(
        "-u",
        "--user-name",
        required=True,
        help="iNaturalist user name",
        type=str,
        env_var="INAT_USER_NAME"
    )
    parser.add(
        "-p",
        "--project-slug",
        required=True,
        help="Slug (short name) of the project to extract",
        type=str,
        env_var="PROJECT_SLUG"
    )
    parser.add(
        "-s",
        "--page-size",
        default=200,
        help="Number of records to retrieve per request. Default: 200. Max: 200. Use lower value for testing.",
        type=int,
        env_var="PAGE_SIZE"
    )
    parser.add(
        "-o",
        "--output-directory",
        default=os.path.join(".","out"),
        help="Directory name for output files.",
        type=str,
        env_var="OUTPUT_DIR"
    )
    parser.add(
        "-l",
        "--last-id",
        default="0",
        help="The last observation ID from a previous download, used to start a fresh download from the next available observation.",
        type=str,
        env_var="LAST_ID"
    )
    parser.add(
        "-i",
        "--input-file",
        help="An input file that will be merged with the downloaded file",
        type=str,
        env_var="INPUT_FILE",
        default=None
    )

    args_parsed = parser.parse_args(args_in)

    return Configuration(
        api_token=args_parsed.api_token,
        log_level=args_parsed.log_level,
        user_name=args_parsed.user_name,
        project_slug=args_parsed.project_slug,
        page_size=args_parsed.page_size,
        output_directory=args_parsed.output_directory,
        last_id=args_parsed.last_id,
        input_file=args_parsed.input_file
    )
