from http import HTTPStatus
import logging
import os
import sys
from time import sleep
from typing import List

from opnieuw import retry

from requests import get
from requests import Response
from requests.exceptions import ConnectionError, HTTPError, Timeout
from requests.packages.urllib3.exceptions import ProtocolError  # type: ignore


from configuration import Configuration


REQUEST_RETRY_COUNT = int(os.environ.get("REQUEST_RETRY_COUNT") or 4)
REQUEST_RETRY_TIMEOUT_SECONDS = int(
    os.environ.get("REQUEST_RETRY_TIMEOUT_SECONDS") or 60
)

logger = logging.getLogger(__name__)


def _build_header(config: Configuration) -> dict:
    headers = {
        "Accept": "application/json",
        "User-Agent": config.user_name,
        "Authentication": config.api_token,
        "Content-Type": "application/json",
    }

    return headers


def _evaluate_response(response: Response):
    logger.info(f"Request URL: {response.url}")
    logger.info(f"Status code: {response.status_code}")

    def _rate_limited():
        logger.warn("Rate limit has been hit")

    def _not_allowed():
        logger.error("Token is expired, please get a new token. Or your account is not authorized")

    def _not_found():
        logger.error("URL not found")

    def _fatal_error():
        logger.fatal(f"A fatal error occurred: {response.text}")
        sys.exit(2)

    switch = {HTTPStatus.OK: lambda: None, HTTPStatus.TOO_MANY_REQUESTS: _rate_limited}
    switch.get(response.status_code, _fatal_error)()


@retry(
    retry_on_exceptions=(ConnectionError, HTTPError, ProtocolError, Timeout),
    max_calls_total=REQUEST_RETRY_COUNT,
    retry_window_after_first_call_in_seconds=REQUEST_RETRY_TIMEOUT_SECONDS,
)
def get_project_data(config: Configuration) -> List[dict]:
    """
    Retrieves all data for a given project, iterating over all available pages.

    Parameters
    ----------
    config: Configuration
        A custom Configuration object containing important settings.

    Returns
    -------
    List[dict]
        A list of observations, each of which is a JSON-like dictionary.
    """
    headers = _build_header(config)
    url = f"https://api.inaturalist.org/v1/observations?pcid=true&project_id={config.project_slug}&per_page={config.page_size}&order_by=id&order=asc&id_above={config.last_id}"

    r = get(url, headers)
    _evaluate_response(r)

    # Honoring iNaturalist's request: "Please keep requests to about 1 per
    # second, and around 10k API requests a day"
    sleep(1)

    response = r.json()

    return response["results"]
