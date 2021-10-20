# BESTLab Platform

One package to access multiple different data sources through their respective API platforms.

## Example Usage

### HOBO Platform

See `hobo_example.py` for a working example which read in the secrets from `.env` file. It requires `python-dotenv` project. Or you can manually input all the secrets in the code by yourself, like the following script:

```python
import json
from bestlab_platform.hobo import HoboAPI


CLIENT_ID = "aaaaa"
CLIENT_SECRET = "bbbbbbbbbbbbb"
USER_ID = "123456"

# Uncomment the following lines to show debug output
#
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
response = hobo_api.get_data(devices, start_time, end_time)
# Pretty print the JSON object from response
print(json.dumps(response, indent=2))
```

### Tuya Platform

WIP, but almost finished.

### eGauge Platform

Not implemented yet.

## API Reference

WIP, but almost finished.

