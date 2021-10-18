#!/usr/bin/env python
# -*- coding: UTF-8 -*-
from dotenv import dotenv_values
import logging
import json
from hobo_platform import HoboAPI, HoboLogger

if __name__ == '__main__':
    config = dotenv_values(".env")
    CLIENT_ID = config["HOBO_CLIENT_ID"]
    CLIENT_SECRET = config["HOBO_CLIENT_SECRET"]
    USER_ID = config["HOBO_USER_ID"]

    # Uncomment the following line to show debug output
    # HoboLogger.setLevel(logging.DEBUG)

    hobo_api = HoboAPI(CLIENT_ID, CLIENT_SECRET, USER_ID)
    print(hobo_api.token_info.access_token)

    devices = [
        config["LOGGER_1"],
        config["LOGGER_2"]
    ]
    start_time = '2021-10-15 00:00:00'
    end_time = '2021-10-15 01:00:00'
    response = hobo_api.get_data(devices, start_time, end_time)
    # Pretty print the JSON object from response
    print(json.dumps(response, indent=2))
