from http import HTTPStatus
import logging
import os
import sys
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
        "Content-Type": "application/json"
    }

    return headers


def _evaluate_response(response: Response):
    logger.info(f"Request URL: {response.url}")
    logger.info(f"Status code: {response.status_code}")

    def _rate_limited():
        logger.warn(f"Rate limit has been hit")

    def _fatal_error():
        logger.fatal(f"A fatal error occurred: {response.text}")
        sys.exit(2)

    switch = {
        HTTPStatus.OK: lambda: None,
        HTTPStatus.TOO_MANY_REQUESTS: _rate_limited
    }
    switch.get(response.status_code, _fatal_error)()

def _get_page(config: Configuration, page_number: int, headers: dict) -> dict:
    url = f"https://api.inaturalist.org/v1/observations?pcid=true&project_id={config.project_slug}&per_page={config.page_size}&order=desc&order_by=created_at&page={page_number}"

    r = get(url, headers)
    _evaluate_response(r)

    return r.json()

def _there_are_more_results(response: dict):
    total = response["total_results"]
    page = response["page"]
    per_page = response["per_page"]

    # Temporary
    if page * per_page > 5:
        return False

    #return page * per_page < total


def get_project_data(config: Configuration) -> List[dict]:
    """
    Retrieves all data for a given project, iterating over all available pages.

    Parameters
    ----------
    config: Configuration
        A custom Configuration object containing important settings

    Returns
    -------
    A list of observations, each of which is a dictionary
    """

    results = list()

    headers = _build_header(config)

    page_number = 1
    response = _get_page(config, page_number, headers)
    results.append(response["results"])

    while _there_are_more_results(response):
        page_number += 1
        response = _get_page(config, page_number, headers)
        results.append(response["results"])

    return response

