BESTLab Platform
================

One package to access multiple different data sources through their
respective API platforms.

Install
-------

In conda or virtualenv environment, run the following commad:

.. code:: bash

   python3 -m pip install -U bestlab_platform

Usage
-----

HOBO Platform
~~~~~~~~~~~~~

Example
^^^^^^^

.. code:: python

   import json
   from bestlab_platform.hobo import HoboAPI


   CLIENT_ID = "aaaaa"
   CLIENT_SECRET = "bbbbbbbbbbbbb"
   USER_ID = "123456"

   # Uncomment the following lines to show all debug output
   #
   # import logging
   # from bestlab_platform.hobo import HoboLogger
   # HoboLogger.setLevel(logging.DEBUG)

   hobo_api = HoboAPI(CLIENT_ID, CLIENT_SECRET, USER_ID)
   print(f"access token: {hobo_api.token_info.access_token}")

   devices = [
       "123456789",
       "987654321"
   ]
   start_time = '2021-10-15 00:00:00'
   end_time = '2021-10-15 01:00:00'
   response = hobo_api.get_data(devices, start_time, end_time, warn_on_empty_data=True)
   # Pretty print the JSON object from response
   print(json.dumps(response, indent=2))

`hobo_example.py <https://github.com/umonaca/bestlab_platform/blob/master/example/hobo_example.py>`__
is another working example which reads in the secrets from a
single\ ``.env`` file. It requires ``python-dotenv`` package.

**Note:** Since HOBO APIs are extremely straightforward, you can
definitely write your own script without any extra packages (including
this one) except for ``requests``\ package. However, there are some
extra functionality provided by this package:

-  exception handling
-  logging with standard format (including timestamps etc.)
-  caching and reusing of existing unexpired access tokens

Tuya Platform
~~~~~~~~~~~~~

This package **correctly and automatically** handles connection, token
caching and refreshing behind the scene so you can focus on your work.
It provides functions to call most of the APIs available on their
platform (available to our project account), and also added
functionalities to:

-  Call API for multiple devices in batch.
-  Query device logs, correctly follows the pagination and return the
   entire log available for the period.

It is inspired by `Tuya’s own python
SDK <https://github.com/tuya/tuya-iot-python-sdk>`__, but their SDK does
not work for our projects, because of the following reasons:

-  It is only suitable for B-to-C scenarios. It uses API endpoints
   **scoped to users within the cloud project**. In order to use these
   endpoints, we have to physically go to where the devices are located
   and add them again with another mobile app, and add those devices
   into the correct “Asset”.
-  It requires subscription to Tuya’s message service, which is over
   complicated.
-  It contains too many APIs that we will never use.
-  It does not have any function to query device logs. Also, Tuya’s API
   to query the device log is paginated, which requires manual handling.

`TinyTuya <https://github.com/jasonacox/tinytuya>`__ is another python
project which uses a simple function to connect and fetch data from the
Tuya IoT cloud. However, their function does not work seamlessly for us
because:

-  Tuya platform never refreshes current access token, unless you use
   the refresh token to get a new one. Access token expires two hours
   later after it is first obtained, which means if we don’t refresh the
   token, we will see an error message.

.. _example-1:

Example
^^^^^^^

.. code:: python

   #!/usr/bin/env python
   # -*- coding: UTF-8 -*-
   """Tuya API"""
   from __future__ import annotations

   import json
   from bestlab_platform.tuya import TuyaOpenAPI, SmartHomeDeviceAPI, TuyaDeviceManager

   HISTORICAL_API = "/v1.0/devices/{}/logs"

   if __name__ == '__main__':
       # Secrets located in .env files
       config = dotenv_values(".env")
       ENDPOINT = "https://openapi.tuyaus.com"
       CLIENT_ID = "aaabbbbcccc"
       CLIENT_SECRET = "dddddddddd12345"

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

       # map of device name (your choice, can be any string, for readability) -> device id (in Tuya's system)
       devices = {
           "PIR3": "asdasdadx",
           "PIR4": "12345abcde"
       }

       # Unix timestamp in your local zone, can be 10 digit or 13 digit int, float, or string
       start_timestamp = "1634005305000"
       end_timestamp = "1634523705000"

       # Example 1: Query in batch
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

       # Example 2: call API for a single device
       # You can use the code above or the following. It's flexible.
       response_device_status = SmartHomeDeviceAPI(tuya_api).get_device_status(devices["PIR3"])
       print(response_device_status)

       response_device_log = SmartHomeDeviceAPI(tuya_api).get_device_log(
           device_id=devices["PIR3"],
           start_timestamp=start_timestamp,
           end_timestamp=end_timestamp,
           device_name="PIR3",
           warn_on_empty_data=True
       )
       print(response_device_log)

`tuya_example.py <https://github.com/umonaca/bestlab_platform/blob/master/example/tuya_example.py>`__
is another working example which reads in the secrets from a
single\ ``.env`` file in your working directory. It requires
``python-dotenv`` package.

eGauge Platform
~~~~~~~~~~~~~~~

Not implemented yet.

API Reference
-------------

https://bestlab-platform.readthedocs.io/en/latest/index.html
