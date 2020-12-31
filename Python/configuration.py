from dataclasses import dataclass
import os
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
        Number of records to retrieve per request. Default: 200. Max: 200. Use lower value for testing.
    output_file: str
        Directory path and name for output file.
    """

    api_token: str
    log_level: str
    user_name: str
    project_slug: str
    page_size: int
    output_file: str


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
        "-l",
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
        "--output-file",
        default=os.path.join(".","out","output.csv"),
        help="Directory path and name for output file.",
        type=str,
        env_var="OUTPUT_FILE"
    )

    args_parsed = parser.parse_args(args_in)

    return args_parsed
