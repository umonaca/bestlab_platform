"""Tuya Open API. Forked and refactored from Tuya SDK https://github.com/tuya/tuya-iot-python-sdk"""

from __future__ import annotations

import hashlib
import hmac
import json
import time
from typing import Any, Dict, Optional, Tuple

import requests

from ..exceptions import ResponseError
from .openlogging import filter_logger, logger

TUYA_ERROR_CODE_TOKEN_INVALID = 1010
GET_TOKEN_API = "/v1.0/token"
REFRESH_TOKEN_API = "/v1.0/token/{}"


class TuyaTokenInfo:
    """Tuya token info.

    Attributes:
        access_token: Access token.
        expire_time: Valid period in seconds.
        refresh_token: Refresh token.
        uid: Tuya user ID.
        # platform_url: user region platform url
    """
    def __init__(self, token_response: Dict[str, Any]):
        """Init TuyaTokenInfo."""
        result = token_response.get("result", {})

        self.expire_time = (
            token_response.get("t", 0)
            + result.get("expire", result.get("expire_time", 0)) * 1000
        )
        self.access_token = result.get("access_token", "")
        self.refresh_token = result.get("refresh_token", "")
        self.uid = result.get("uid", "")
        # self.platform_url = result.get("platform_url", "")


class TuyaOpenAPI:
    """Open Api.

    Typical usage example:

    openapi = TuyaOpenAPI(ENDPOINT, ACCESS_ID, ACCESS_KEY)
    """
    def __init__(
        self,
        endpoint: str,
        access_id: str,
        access_secret: str,
        lang: str = "en",
        auto_connect: bool = True
    ):
        """Init TuyaOpenAPI."""
        self.session = requests.session()

        self.endpoint = endpoint
        self.access_id = access_id
        self.access_secret = access_secret
        self.lang = lang

        self.__login_path = GET_TOKEN_API
        self.__refresh_token_path = REFRESH_TOKEN_API

        self.token_info: TuyaTokenInfo | None = None
        if auto_connect:
            self.connect()

    # https://developer.tuya.com/docs/iot/open-api/api-reference/singnature?id=Ka43a5mtx1gsc
    def _calculate_sign(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
    ) -> Tuple[str, int]:

        # HTTPMethod
        str_to_sign = method
        str_to_sign += "\n"

        # Content-SHA256
        content_to_sha256 = (
            "" if body is None or len(body.keys()) == 0 else json.dumps(body)
        )

        str_to_sign += (
            hashlib.sha256(content_to_sha256.encode(
                "utf8")).hexdigest().lower()
        )
        str_to_sign += "\n"

        # Header
        str_to_sign += "\n"

        # URL
        str_to_sign += path

        if params is not None and len(params.keys()) > 0:
            str_to_sign += "?"

            query_builder = ""
            params_keys = sorted(params.keys())

            for key in params_keys:
                query_builder += f"{key}={params[key]}&"
            str_to_sign += query_builder[:-1]

        # Sign
        t = int(time.time() * 1000)

        message = self.access_id
        if self.token_info is not None:
            message += self.token_info.access_token
        message += str(t) + str_to_sign
        sign = (
            hmac.new(
                self.access_secret.encode("utf8"),
                msg=message.encode("utf8"),
                digestmod=hashlib.sha256,
            )
            .hexdigest()
            .upper()
        )
        return sign, t

    def _refresh_access_token_if_need(self, path: str) -> None:
        if path.startswith(self.__login_path):
            return

        if path.startswith(self.__refresh_token_path):
            return

        if self.token_info is None:
            self.connect()
            return

        # should use refresh token?
        now = int(time.time() * 1000)
        expired_time = self.token_info.expire_time

        if expired_time - 60 * 1000 > now:  # 1min
            return

        self.token_info.access_token = ""
        response = self.get(
            self.__refresh_token_path.format(self.token_info.refresh_token)
        )

        self.token_info = TuyaTokenInfo(response)

    def connect(
        self
    ) -> Dict[str, Any]:
        """Connect to Tuya Cloud.

        Returns:
            response: connect response
        """
        # Fix signature invalid bug when the user explicitly calls connect()
        self.token_info = None
        response = self.get(
            path=GET_TOKEN_API,
            params={
                "grant_type": 1
            }
        )

        # Cache token info.
        self.token_info = TuyaTokenInfo(response)

        return response

    def is_connect(self) -> bool:
        """Whether we have an access token.
        Note: will return true even if the access token is expired.
        Token refreshing is handled internally.
        """
        return self.token_info is not None and len(self.token_info.access_token) > 0

    def __request(
        self,
        method: str,
        path: str,
        params: Optional[Dict[str, Any]] = None,
        body: Optional[Dict[str, Any]] = None,
    ) -> dict[str, Any]:
        """Internal method to sign and send.
        You should avoid using this method directly.

        Args:
            method (str): HTTP method
            path (str): relative path starting with "/"
            params (Optional[Dict[str, Any]]): HTTP parameters
            body (Optional[Dict[str, Any]]): HTTP body

        Returns:
            JSON decoded response (a dict).

        Raises:
            ResponseError: HTTP status code and response text
        """
        self._refresh_access_token_if_need(path)

        access_token = self.token_info.access_token if self.token_info else ""
        sign, t = self._calculate_sign(method, path, params, body)
        headers = {
            "client_id": self.access_id,
            "sign": sign,
            "sign_method": "HMAC-SHA256",
            "access_token": access_token,
            "t": str(t),
            "lang": self.lang,
        }

        logger.debug(
            f"Request: method = {method}, "
            f"url = {self.endpoint + path}, "
            f"params = {params}, "
            f"body = {filter_logger(body)}, "
            f"t = {int(time.time()*1000)}"
        )

        response = self.session.request(
            method, self.endpoint + path, params=params, json=body, headers=headers
        )

        # Tuya returns HTTP 200 OK even if there is an error.
        # They use their own error code to indicate the error.
        if response.ok is False or response.json().get("success", False) is False:
            # Retry
            logger.warning(
                f"Response error, trying to reconnect: "
                f"code={response.status_code}, "
                f"body={response.text}, "
                f"t = {int(time.time() * 1000)}"
            )
            self.token_info = None
            response = self.session.request(
                method, self.endpoint + path, params=params, json=body, headers=headers
            )
            # Somehow failed again.
            if response.ok is False or response.json().get("success", False) is False:
                logger.error(
                    f"Response error: code={response.status_code}, body={response.text}"
                )
                raise ResponseError(response.status_code, response.text)
            # otherwise persist the response

        result: dict[str, Any] = response.json()

        logger.debug(
            f"Response: {json.dumps(filter_logger(result), ensure_ascii=False, indent=2)}"
        )

        return result

    def get(
        self, path: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Http Get.

        Requests the server to return specified resources.

        Args:
            path (str): api path
            params (map): request parameter

        Returns:
            response: response body
        """
        return self.__request("GET", path, params, None)

    def post(
        self, path: str, body: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Http Post.

        Requests the server to update specified resources.

        Args:
            path (str): api path
            body (map): request body

        Returns:
            response: response body
        """
        return self.__request("POST", path, None, body)

    def put(
        self, path: str, body: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Http Put.

        Requires the server to perform specified operations.

        Args:
            path (str): api path
            body (map): request body

        Returns:
            response: response body
        """
        return self.__request("PUT", path, None, body)

    def delete(
        self, path: str, params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Http Delete.

        Requires the server to delete specified resources.

        Args:
            path (str): api path
            params (map): request param

        Returns:
            response: response body
        """
        return self.__request("DELETE", path, params, None)
