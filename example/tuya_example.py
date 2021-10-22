#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Tuya API"""
from __future__ import annotations

import json
from dotenv import dotenv_values
from bestlab_platform.tuya import TuyaOpenAPI, SmartHomeDeviceAPI, TuyaDeviceManager

HISTORICAL_API = "/v1.0/devices/{}/logs"

if __name__ == '__main__':
    # Secrets located in .env files
    config = dotenv_values(".env")
    ENDPOINT = "https://openapi.tuyaus.com"
    CLIENT_ID = config["CLIENT_ID"]
    CLIENT_SECRET = config["CLIENT_SECRET"]

    # Uncomment the following line to print messages when querying device logs on Tuya platform
    #
    # import logging
    # from bestlab_platform.tuya import TUYA_LOGGER
    # TUYA_LOGGER.setLevel(logging.INFO)
    #
    # If you want to debug requests and responses, uncomment the following line.
    # TUYA_LOGGER.setLevel(logging.DEBUG)

    tuya_api = TuyaOpenAPI(ENDPOINT, CLIENT_ID, CLIENT_SECRET)
    print(tuya_api.token_info.access_token)

    # map of device name (your choice, can be string) -> device id in Tuya's system
    # devices = {
    #     "PIR3": "asdasdadx",
    #     "PIR4": "12345abcde"
    # }
    device_names = ["PIR3", "PIR4", "PIR5", "PIR6"]
    devices = {}
    for name in device_names:
        devices[name] = config[name]

    # Unix timestamp in your local zone, can be 10 digit or 13 digit int, float, or string
    start_timestamp = "1634005305000"
    end_timestamp = "1634523705000"

    # Query in batch
    device_group = TuyaDeviceManager(tuya_api, device_map=devices)
    devices_log_map = device_group.get_device_log_in_batch(
        start_timestamp=start_timestamp,
        end_timestamp=end_timestamp,
        warn_on_empty_data=True
    )

    # Save to JSON files
    for dev_name, device_log in devices_log_map.items():
        with open(f'{dev_name}_historical_1017.json', 'w') as f:
            json.dump(device_log, f)
