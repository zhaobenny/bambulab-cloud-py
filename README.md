# bambulab-cloud-py

> Python implementation of [bambulab-rs](https://github.com/m1guelpf/bambulab-rs)

An unofficial Python client for Bambulab's Cloud API.

# 🛠️ Usage
```python
from bambulab_cloud import BambuClient

client = await BambuClient.login(email, password)
profile = await client.get_profile()
print(profile)
devices = await client.get_devices()
print(devices)
tasks = await client.get_tasks()
print(tasks)
```
Supported calls so far are just `GET` requests for data.

## License
[MIT](https://github.com/zhaobenny/bambulab-cloud-py/blob/main/LICENSE)
