"""HOBO API"""

from __future__ import annotations

import json
import logging
import time
from typing import Any, List, Optional, Union

import requests

from ..exceptions import ResponseError

# https://docs.python.org/3/howto/logging.html#logging-basic-tutorial
logger = logging.getLogger('hobo_iot')
# logger.setLevel(logging.DEBUG)
default_handler = logging.StreamHandler()
default_handler.setFormatter(logging.Formatter(
    "[%(asctime)s] [hobo-%(module)s] %(message)s"
))
logger.addHandler(default_handler)
HoboLogger = logger

HOBO_ENDPOINT = "https://webservice.hobolink.com"
HOBO_GET_TOKEN_API = "/ws/auth/token"


class HoboTokenInfo:
    """Hobo token info.

    Attributes:
        access_token: Access token.
        token_type: "bearer".
        expire_time: Time in seconds when the token will be expired.
    """
    def __init__(self, token_response: dict[str, Any]):
        """Init HoboTokenInfo."""

        self.access_token = token_response.get("access_token", "")
        self.token_type = token_response.get("token_type", "bearer")
        self.expire_time = (
            time.time()
            + token_response.get("expires_in", 600)
        )

    def need_refresh(self) -> bool:
        """Should we get a new the token?"""
        if self.access_token:
            return time.time() + 60 > self.expire_time  # type: ignore
        else:
            return True


class HoboAPI:
    """HOBO API

    Example:
        hobo_api = HoboAPI(client_id, client_secret, user_id)
        hobo_api.get_data(["1234567", "8912345"], start_date_time, end_date_time)
    """
    def __init__(
            self,
            client_id: str,
            client_secret: str,
            user_id: int | str,
            endpoint: str = HOBO_ENDPOINT
    ):
        self.endpoint = endpoint
        self.client_id = client_id
        self.client_secret = client_secret
        self.user_id = str(user_id)

        self.session = requests.session()

        self.token_info: HoboTokenInfo | None = None
        self._get_access_token_if_needed(force=True)

    def get_data(
        self,
        loggers: List[Union[str, int]] | Union[str, int],
        start_date_time: str,
        end_date_time: str,
        warn_on_empty_data: bool = False
    ) -> dict[str, Any]:
        """Get data from HOBO Web Services

        Args:
            loggers (List[Union[str, int]] | Union[str, int]):
                A list of Device IDs, or a single comma separated string of device ids.
            start_date_time (str):
                Must be in yyyy-MM-dd HH:mm:ss format
            end_date_time (str):
                Must be in yyyy-MM-dd HH:mm:ss format
            warn_on_empty_data (bool):
                If True, print a warning message (to HoboLogger, which by default is your console).
                Has no effect on function return.

        Returns:
            response (dict): JSON decoded response

        Raises:
            TypeError:
                The "loggers" parameter type is incorrect
        """
        # Comma separated list of logger device IDs
        logger_list: str = ""
        if isinstance(loggers, str):
            logger_list = loggers
        elif isinstance(loggers, list):
            logger_list = ",".join((str(id) for id in loggers))
        else:
            raise TypeError('Please check your input to get_data function')

        params = {
            "loggers": logger_list,
            "start_date_time": start_date_time,
            "end_date_time": end_date_time
        }

        response = self.get(
            path=f"/ws/data/file/JSON/user/{self.user_id}",
            params=params
        )

        if warn_on_empty_data and not response.get('observation_list', None):
            logger.warning(f"The data seems to be empty. Response: {response}, t = {int(time.time())}")

        return response

    def _get_access_token_if_needed(self, force: bool = False) -> None:
        """Get a new token if needed

        Args:
            force (bool): do not cache old token

        Raises:
            ResponseError: HTTP status code and response text
        """
        if not force and self.token_info and not self.token_info.need_refresh():
            return

        payload = {
            "grant_type": "client_credentials",
            "client_id": self.client_id,
            "client_secret": self.client_secret
        }

        logger.debug(f"Getting new token, t = {int(time.time())}")

        logger.debug(
            f"Request: method = POST, \
                 url = {self.endpoint + HOBO_GET_TOKEN_API},\
                 params = None,\
                 body = {payload},\
                 t = {int(time.time())}"
        )

        response: requests.Response = self.session.post(
            url=self.endpoint + HOBO_GET_TOKEN_API,
            data=payload
        )

        if response.ok is False:
            logger.error(
                f"Response error: code={response.status_code}, body={response.text}"
            )
            raise ResponseError(response.status_code, response.text)

        self.token_info = HoboTokenInfo(response.json())

    def __request(
        self,
        method: str,
        path: str,
        params: Optional[dict[str, Any]] = None,
        body: Optional[dict[str, Any]] = None,
        auth_required: bool = True
    ) -> dict[str, Any]:
        """Internal method to call requests package

        Args:
            method (str):
                GET or POST
            path (str):
                Example: '/ws/data/file/JSON/user/13751'
            params (map):
                Request parameter
            body (map):
                Request body, passed to "data" parameter of requests.post

        Returns:
            response (dict): JSON decoded response body

        Raises:
            ResponseError: HTTP status code and response text
        """
        if auth_required:
            self._get_access_token_if_needed()

        headers = None
        if self.token_info:
            access_token = self.token_info.access_token
            headers = {"Authorization": f"Bearer {access_token}"}

        logger.debug(
            f"Request: method = {method}, \
                url = {self.endpoint + path},\
                params = {params},\
                body = {body},\
                t = {int(time.time())}"
        )

        response = self.session.request(
            method, self.endpoint + path, params=params, data=body, headers=headers
        )

        if response.ok is False:
            logger.error(
                f"Response error: code={response.status_code}, body={response.text}"
            )
            raise ResponseError(response.status_code, response.text)

        result: dict[str, Any] = response.json()

        logger.debug(
            f"Response: {json.dumps(result, ensure_ascii=False, indent=2)}"
        )

        return result

    def get(
        self, path: str, params: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Http Get.

        Requests the server to return specified resources.

        Args:
            path (str): api path
            params (map): request parameter

        Returns:
            response (dict): JSON decoded response body
        """
        return self.__request(method="GET", path=path, params=params, body=None)

    def post(
        self, path: str, body: Optional[dict[str, Any]] = None
    ) -> dict[str, Any]:
        """Http Post.

        Requests the server to update specified resources.

        Args:
            path (str): api path
            body (map): request body

        Returns:
            response (dict): JSON decoded response body
        """
        return self.__request(method="POST", path=path, params=None, body=body)
