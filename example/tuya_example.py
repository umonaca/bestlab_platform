#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Tuya API"""

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from __future__ import annotations

from typing import Any, List
import logging
from bestlab_platform.tuya import TUYA_LOGGER

import json
from dotenv import dotenv_values
from bestlab_platform.tuya import TuyaOpenAPI, SmartHomeDeviceAPI

HISTORICAL_API = "/v1.0/devices/{}/logs"
TUYA_LOGGER.setLevel(logging.INFO)


def get_devices_historical_data_in_batch(api, device_map, start_timestamp, end_timestamp, warn_on_empty_data=True):
    """TODO: Refactor into tuya_platform package"""
    for device_name, device_id in device_map.items():
        device_logs = SmartHomeDeviceAPI(api).get_device_log(
            device_id,
            start_timestamp,
            end_timestamp,
            device_name=device_name,
            warn_on_empty_data=warn_on_empty_data
        )

        with open(f'{device_name}_historical_1017.json', 'w') as f:
            json.dump(device_logs, f)


if __name__ == '__main__':
    # Secrets located in .env files
    config = dotenv_values(".env")
    ENDPOINT = "https://openapi.tuyaus.com"
    CLIENT_ID = config["CLIENT_ID"]
    CLIENT_SECRET = config["CLIENT_SECRET"]

    # Uncomment the following line to show debug output
    #
    # import logging
    # from bestlab_platform.tuya import TUYA_LOGGER
    # TUYA_LOGGER.setLevel(logging.DEBUG)

    tuya_api = TuyaOpenAPI(ENDPOINT, CLIENT_ID, CLIENT_SECRET)
    print(tuya_api.token_info.access_token)

    device_names = ["PIR3", "PIR4", "PIR5", "PIR6"]
    devices = {}
    for name in device_names:
        devices[name] = config[name]

    start_timestamp = "1634005305000"
    end_timestamp = "1634523705000"

    get_devices_historical_data_in_batch(tuya_api, devices, start_timestamp, end_timestamp, warn_on_empty_data=True)
