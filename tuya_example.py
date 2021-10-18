#!/usr/bin/env python
# -*- coding: UTF-8 -*-
"""Tuya API"""

# Press Shift+F10 to execute it or replace it with your code.
# Press Double Shift to search everywhere for classes, files, tool windows, actions, and settings.

from __future__ import annotations

import logging
import json
from dotenv import dotenv_values
from tuya_platform import TuyaOpenAPI
from tuya_platform.openlogging import TUYA_LOGGER as logger

HISTORICAL_API = "/v1.0/devices/{}/logs"


def get_historical_data(
        api: TuyaOpenAPI,
        device_id: str,
        start_time: int | float | str,
        end_time: int | float | str,
        size: int = 100,
        type_: int = 7
):
    """TODO: Merge into tuya_platform package"""
    params = {
        "type": type_,
        "start_time": str(start_time),
        "end_time": str(end_time),
        "size": size
    }
    first_page = api.get(path=HISTORICAL_API.format(device_id), params=params)
    yield first_page["result"]["logs"]

    if first_page["result"]["has_next"]:
        flag = True
        current_page = first_page
        while flag:
            params["start_row_key"] = current_page["result"]["next_row_key"]
            next_page = api.get(path=HISTORICAL_API.format(device_id), params=params)
            yield next_page["result"]["logs"]

            current_page = next_page
            if not current_page["result"]["has_next"]:
                flag = False


def get_devices_historical_data(api, devices, start_time, end_time):
    """TODO: Refactor into tuya_platform package"""
    for device_name, device_id in devices.items():
        print(device_name)
        page_num = 0
        logs: list = []
        for page in get_historical_data(tuya_api, device_id, start_timestamp, end_timestamp):
            page_num += 1
            print(page)
            print(page_num)
            logs = logs + page

        with open(f'{device_name}_historical_1017.json', 'w') as f:
            json.dump(logs, f)


if __name__ == '__main__':
    # Secrets located in .env files
    config = dotenv_values(".env")
    ENDPOINT = "https://openapi.tuyaus.com"
    CLIENT_ID = config["CLIENT_ID"]
    CLIENT_SECRET = config["CLIENT_SECRET"]

    # Uncomment the following line to show debug output
    # logger.setLevel(logging.DEBUG)

    tuya_api = TuyaOpenAPI(ENDPOINT, CLIENT_ID, CLIENT_SECRET)
    tuya_api.connect()
    print(tuya_api.token_info.access_token)

    device_names = ["PIR3", "PIR4", "PIR5", "PIR6"]
    devices = {}
    for name in device_names:
        devices[name] = config[name]

    start_timestamp = "1634005305000"
    end_timestamp = "1634523705000"

    get_devices_historical_data(tuya_api, devices, start_timestamp, end_timestamp)
