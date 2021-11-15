"""Tuya device api. Forked and refactored from https://github.com/tuya/tuya-iot-python-sdk"""

from __future__ import annotations

from typing import Any, Iterator, Optional

from .openapi import TuyaOpenAPI
from .openlogging import logger


class SmartHomeDeviceAPI:
    """Tuya Smart Home Device API.
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

        See also:
        https://iot.tuya.com/cloud/explorer?id=p1622082860767nqhjxa&groupId=group-home&interfaceId=470224763027539

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

    def _yield_device_log_page(
            self,
            device_id: str,
            start_time: int | float | str,
            end_time: int | float | str,
            size: int = 100,
            type_: int = 7,
            warn_on_empty_data: bool = False
    ) -> Iterator[list[Any]]:
        """Since device log API is paginated, this function returns an iterator which yields results within a page
        for the given device.
        You should avoid calling this function directly unless you know what you are doing. Please call
        get_device_log() instead. This function is designed to be called by get_device_log().

        Args:
            device_id (str):
                Device ID.
            start_time (int | float | str):
                Start timestamp for log to be queried. Note that free version of Tuya only keeps one week's data.
            end_time (int | float | str):
                End timestamp for log to be queried. Note that free version of Tuya only keeps one week's data.
            size (int):
                Page size. Although not documented anywhere, Tuya's limit for page size is <= 100.
            type_ (int):
                Usually this field should be 7.
                See https://developer.tuya.com/en/docs/cloud/device-management?id=K9g6rfntdz78a#sjlx1
            warn_on_empty_data (bool):
                Print a warning message to the logger. Default: False.

        Returns:
            An iterator which produces one page's result each time. Stops when there are no more pages.
        """
        params = {
            "type": type_,
            "start_time": str(start_time),
            "end_time": str(end_time),
            "size": size
        }
        first_page = self.api.get(path=f"/v1.0/devices/{device_id}/logs", params=params)

        # Warn on empty result if warn_on_empty_data = True
        if warn_on_empty_data and not first_page["result"]["logs"]:
            logger.warning(f"Detected empty result. device: {device_id}, params: {str(params)}")

        yield first_page["result"]["logs"]

        if first_page["result"]["has_next"]:
            flag = True
            current_page = first_page
            while flag:
                params["start_row_key"] = current_page["result"]["next_row_key"]
                next_page = self.api.get(path=f"/v1.0/devices/{device_id}/logs", params=params)
                yield next_page["result"]["logs"]

                current_page = next_page
                if not current_page["result"]["has_next"]:
                    flag = False

    def get_device_log(
            self,
            device_id: str,
            start_timestamp: int | float | str,
            end_timestamp: int | float | str,
            device_name: Optional[str] = None,
            warn_on_empty_data: bool = False,
            type_: int = 7
    ) -> list[Any]:
        """Get device log stored on the Tuya platform. Note that free version of Tuya Platform only stores 7 days' data.

        Args:
            device_id (str):
                Device ID.
            start_timestamp (int | float | str):
                Start timestamp for log to be queried. Must be an 10 digit or 13 digit unix timestamp.
                Note that free version of Tuya only keeps one week's data.
            end_timestamp (int | float | str):
                End timestamp for log to be queried. Must be an 10 digit or 13 digit unix timestamp
                Note that free version of Tuya only keeps one week's data.
            device_name (str):
                User friendly name for your convenience. It can be any string you like, such as "PIR3"
            warn_on_empty_data (bool):
                If True, print a warning message to the logger an empty page or empty final result is detected.
                Default: False.
            type_ (int):
                Usually this field should be 7 ("the actual data" from the device), unless you want something else.
                See https://developer.tuya.com/en/docs/cloud/device-management?id=K9g6rfntdz78a#sjlx1

        Returns:
            A list of device logs. Note that the return type is not a dictionary and is not the raw response, because
            multiple page is expected.
        """
        result_device_name = device_name if device_name else device_id
        logger.info(f"Start fetching historical data for device {result_device_name}")
        page_num = 1
        device_logs: list[Any] = []
        for page in self._yield_device_log_page(
                device_id,
                start_timestamp,
                end_timestamp,
                warn_on_empty_data=warn_on_empty_data,
                type_=type_
        ):
            logger.info(f"Fetched historical data for device {result_device_name}, page {page_num}")
            page_num += 1
            device_logs = device_logs + page

        # Warn on empty result if warn_on_empty_data = True
        if warn_on_empty_data and not device_logs:
            logger.warning(f"Detected empty result for device {str(result_device_name)}")

        return device_logs


class TuyaDeviceManager:
    """Manages multiple devices and provides functions to call APIs for all devices in batch
    Note: This is different from upstream Tuya SDK.
    """

    def __init__(
        self,
        api: TuyaOpenAPI,
        device_map: Optional[dict[str, str]] = None,
        device_list: Optional[list[str]] = None
    ):
        if (not device_map and not device_list) or (device_map and device_list):
            raise ValueError("You mut specify either device_map or device_list")

        self.api = api

        if device_map:
            self.device_map: dict[str, str] = device_map
            self.device_idsL: list[str] = list(device_map.values())
        elif device_list:
            self.device_map: dict[str, str] = {device_id: device_id for device_id in device_list}  # type: ignore
            self.device_ids: list[str] = device_list
        else:
            raise ValueError("You must specify either device_map or device_list")

    def get_device_status_in_batch(self) -> dict[str, Any]:
        """Get device status for all devices in this instance in batch

        Returns:
            API response in a dictionary.
        """
        response = SmartHomeDeviceAPI(self.api) \
            .get_device_list_status(self.device_ids)
        return response

    def get_device_log_in_batch(
            self,
            start_timestamp: int | float | str,
            end_timestamp: int | float | str,
            warn_on_empty_data: bool = False,
            type_: int = 7
    ) -> dict[str, Any]:
        """Get device log stored on the Tuya platform. Note that free version of Tuya Platform only stores 7 days' data.

        Args:
            start_timestamp (int | float | str):
                Start timestamp for log to be queried. Must be an 10 digit or 13 digit unix timestamp.
                Note that free version of Tuya only keeps one week's data.
            end_timestamp (int | float | str):
                End timestamp for log to be queried. Must be an 10 digit or 13 digit unix timestamp
                Note that free version of Tuya only keeps one week's data.
            warn_on_empty_data (bool):
                If True, print a warning message to the logger an empty page or empty final result is detected.
                Default: False.
            type_ (int):
                Usually this field should be 7 ("the actual data" from the device), unless you want something else.
                See https://developer.tuya.com/en/docs/cloud/device-management?id=K9g6rfntdz78a#sjlx1

        Returns:
            Map of device name -> device log.
        """
        devices_log_map = {}
        for device_name, device_id in self.device_map.items():
            device_log = SmartHomeDeviceAPI(self.api).get_device_log(
                device_id,
                start_timestamp=start_timestamp,
                end_timestamp=end_timestamp,
                device_name=device_name,
                warn_on_empty_data=warn_on_empty_data,
                type_=type_
            )
            devices_log_map[device_name] = device_log

        return devices_log_map

    def get_device_info_in_batch(self, include_device_status: bool = True) -> dict[str, Any]:
        """Get device info in batch

        Args:
            include_device_status (bool): Include device status in the return fields. Default: True

        Returns:
            API response in a dictionary.
        """
        response = SmartHomeDeviceAPI(self.api).get_device_list_info(
            self.device_ids, include_device_status=include_device_status
        )
        return response

    def get_factory_info_in_batch(self) -> dict[str, Any]:
        """"Query the factory information of the devices.
        Possible return fields are: id, uuid, sn, mac.

        Returns:
            API response in a dictionary.
        """
        response = SmartHomeDeviceAPI(self.api) \
            .get_factory_info(self.device_ids)
        return response

    def send_command_in_batch(self, commands: list[dict[str, Any]]) -> dict[str, Any]:
        """Issue standard instructions to control equipments.

        Args:
            commands (list): issue commands.

        Returns:
            API response in a dictionary.
        """
        device_response_map: dict[str, Any] = {}
        for device_name, device_id in self.device_map.items():
            device_response = SmartHomeDeviceAPI(self.api).send_commands(device_id, commands)
            device_response_map[device_name] = device_response

        return device_response_map
