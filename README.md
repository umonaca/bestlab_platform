# BESTLab Platform

One package to access multiple different data sources through their respective API platforms.

## Usage

### HOBO Platform

Example:

```python
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
```

[hobo_example.py](https://github.com/umonaca/bestlab_platform/blob/master/example/hobo_example.py) is another working example which reads in the secrets from a single`.env` file. It requires `python-dotenv` package. 

**Note:** Since HOBO APIs are extremely straightforward, you can definitely write your own script without any extra packages (including this one) except for `requests`package. However, there are some extra functionality provided by this package:

- exception handling
- logging with standard format (including timestamps etc.)
- caching and reusing of existing unexpired access tokens

### Tuya Platform

WIP, but almost finished.

### eGauge Platform

Not implemented yet.

## API Reference

WIP, but almost finished.

