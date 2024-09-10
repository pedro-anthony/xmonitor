# Xmonitor

## Overview
This script periodically queries XMRig worker statistics from the specified URLs and displays their performance metrics in a tabulated format. It helps users monitor their mining operations by providing real-time data on hashrate, CPU model, memory usage, and system load.

## How to Use

### Requirements

- Python 3.x
- Requests
- Tabulate
- Colorama


You can install the required packages just by running poetry, which will then create an ENV you can use:

```bash
$ poetry install
$ poetry shell
```

### Configuration
Configure your XMRig workers to enable the http API (Tokens and unrestricted access are currently not supported)
```json
"http": {
        "enabled": true,
        "host": "0.0.0.0",
        "port": 5200,
        "access-token": null,
        "restricted": true
}
```

Create a `workers.json` file in the same directory as the script. This file should contain the URLs of the mining workers you want to monitor
```json
"urls": [
	"http://127.0.10.1:5200/2/summary"
	]
```
Run the script inside the poetry environment
```bash
$ python main.py
```