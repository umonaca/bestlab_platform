"""Tuya device api. Forked and refactored from https://github.com/tuya/tuya-iot-python-sdk"""

from __future__ import annotations

from typing import Any, Literal, Optional
from .openapi import TuyaOpenAPI
from .openlogging import logger


class SmartHomeDeviceAPI:
    """Call Tuya Smart Home Device API directly.
    See https://developer.tuya.com/en/docs/cloud/device-management?id=K9g6rfntdz78a for the list of APIs.

    Example:
        tuya_api = tuya_api = TuyaOpenAPI("https://openapi.tuyaus.com", CLIENT_ID, CLIENT_SECRET)
        device_api = SmartHomeDeviceAPI(tuya_api)
        print(device_api.get_device_status("YOUR_DEVICE_ID_HERE"))
    """

    def __init__(self, api: TuyaOpenAPI):
        self.api = api

    def get_device_info(self, device_id: str, include_device_status: bool = True) -> dict[str, Any]:
        """Get device details, including properties and the latest status of the device.

        Args:
            device_id (str): Device ID
            include_device_status (bool): Whether device status field should be included. Default: True

        Returns:
            API Response in a dictionary.
        """
        response = self.api.get(f"/v1.0/devices/{device_id}")
        if not include_device_status:
            response["result"].pop("status")
        return response

    def get_device_list_info(self, device_ids: list[str], include_device_status: bool = True) -> dict[str, Any]:
        """Get device info for a list of devices.

        Args:
            device_ids (list[str]): a list of device ids.
            include_device_status: Include device status in the return fields. Default: True

        Returns:
            API Response in a dictionary.
        """
        response = self.api.get("/v1.0/devices/", {"device_ids": ",".join(device_ids)})
        if response["success"] and not include_device_status:
            for info in response["result"]["devices"]:
                info.pop("status")
        # response["result"]["list"] = response["result"]["devices"]
        return response

    def get_device_status(self, device_id: str) -> dict[str, Any]:
        """Get device status

        Args:
            device_id (str): Device ID

        Returns:
            API Response in a dictionary.
        """
        response = self.api.get(f"/v1.0/devices/{device_id}")
        response["result"] = response["result"]["status"]
        return response

    def get_device_list_status(self, device_ids: list[str]) -> dict[str, Any]:
        """Get device status for a list of devices.

        Args:
            device_ids (list[str]): List of Device IDs.

        Returns:
            API Response in a dictionary.
        """
        response = self.api.get("/v1.0/devices/", {"device_ids": ",".join(device_ids)})
        status_list = []
        if response["success"]:
            for info in response["result"]["devices"]:
                status_list.append({"id": info["id"], "status": info["status"]})

        response["result"] = status_list
        return response

    def get_factory_info(self, device_ids: list[str]) -> dict[str, Any]:
        """Query the factory information of the device.
        Possible return fields are: id, uuid, sn, mac.

        Args:
            device_ids (list[str]): List of Device IDs.

        Returns:
            API Response in a dictionary.
        """
        return self.api.get(
            "/v1.0/devices/factory-infos", {"device_ids": ",".join(device_ids)}
        )

    # def factory_reset(self, device_id: str) -> dict[str, Any]:
    #     return self.api.post(f"/v1.0/devices/{device_id}/reset-factory")

    # def remove_device(self, device_id: str) -> dict[str, Any]:
    #     return self.api.delete(f"/v1.0/devices/{device_id}")

    def get_device_functions(self, device_id: str) -> dict[str, Any]:
        """Get the instruction set supported by the device, and the obtained instructions can be used to issue control.

        Args:
            device_id (str): Device ID.

        Returns:
            API Response in a dictionary.
        """
        return self.api.get(f"/v1.0/devices/{device_id}/functions")

    def get_category_functions(self, category_id: str) -> dict[str, Any]:
        """Query the instruction set supported by Tuya Platform in the given category.
        You should not need this unless you are a platform developer.

        See also: https://iot.tuya.com/cloud/explorer?id=p1622082860767nqhjxa&groupId=group-home&interfaceId=470224763027539

        Args:
            category_id (str): Product category.

        Returns:
            API Response in a dictionary.
        """
        return self.api.get(f"/v1.0/functions/{category_id}")

    # https://developer.tuya.com/en/docs/cloud/device-control?id=K95zu01ksols7#title-27-Get%20the%20specifications%20and%20properties%20of%20the%20device%2C%20including%20the%20instruction%20set%20and%20status%20set
    def get_device_specification(self, device_id: str) -> dict[str, str]:
        """Acquire the instruction set and status set supported by the device according to the device ID.

        Args:
            device_id (str): Device ID.

        Returns:
            API Response in a dictionary.
        """
        return self.api.get(f"/v1.0/devices/{device_id}/specifications")

    # def get_device_stream_allocate(
    #     self, device_id: str, stream_type: Literal["flv", "hls", "rtmp", "rtsp"]
    # ) -> Optional[str]:
    #     """Get the live streaming address by device ID and the video type.
    #     These live streaming video protocol types are available: RTSP, HLS, FLV, and RTMP.
    #     https://developer.tuya.com/en/docs/cloud/iot-video-live-stream?id=Kaiuybz0pzle4
    #     """
    #     response = self.api.post(
    #         f"/v1.0/devices/{device_id}/stream/actions/allocate", {"type": stream_type}
    #     )
    #     if response["success"]:
    #         return response["result"]["url"]
    #     return None

    def send_commands(
        self, device_id: str, commands: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Issue standard instructions to control equipment

        Args:
            device_id (str): Device ID.
            commands: issue commands.

        Returns:
            API Response in a dictionary.
        """
        return self.api.post(
            f"/v1.0/devices/{device_id}/commands", {"commands": commands}
        )
