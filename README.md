# Flowlink Unmanaged Workload Maker

Automatically creates Unmanaged Workloads (UMWLs) on the Illumio PCE based on IP addresses discovered in FlowLink log files.

[FlowLink](https://docs.illumio.com) is the Illumio Core PCE Flow Collector. It sends flows to the PCE and injects flows for managed and unmanaged workloads. This script monitors the FlowLink log file and automatically creates unmanaged workloads for any new IP addresses found within configured networks.

## Prerequisites

- Python 3.6+
- An Illumio PCE with API access (service account or API key)

## Installation

1. Clone the repository and navigate to the project directory:
    ```bash
    cd illumio-flowlink-umwl-maker
    ```
2. Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```

## Configuration

The script can be configured via command-line arguments or environment variables:

| Argument | Environment Variable | Default | Description |
|---|---|---|---|
| `--pce_host` | `PCE_HOST` | `poc1.illum.io` | PCE hostname |
| `--pce_port` | `PCE_PORT` | `443` | PCE TCP port |
| `--org_id` | `PCE_ORG` | `1` | PCE organization ID |
| `--api_user` | `PCE_API_USER` | *required* | API user / service account |
| `--api_key` | `PCE_API_KEY` | *required* | API key / secret |
| `--log_file` | | *required* | Path to the FlowLink log file to monitor |
| `--networks` | | `192.168.0.0/16,172.16.0.0/12,10.0.0.0/8` | Comma-separated list of networks to match |
| `--max-workloads` | | `0` (unlimited) | Max workloads to create per batch of discovered IPs |
| `--simulate` | | `false` | Simulate workload creation without making changes |
| `--notail` | | `false` | Read the log file from the beginning instead of tailing |
| `--verbose` | | `false` | Enable debug-level logging |

## Usage

```bash
python flowlink-umwl-maker.py \
  --pce_host your_pce_host \
  --api_user your_api_user \
  --api_key your_api_key \
  --log_file /var/log/flowlink.log \
  --networks 10.0.0.0/8,172.16.0.0/12
```

By default the script tails the log file (starts reading from the end and waits for new entries). Use `--notail` to process the entire file from the beginning.

Use `--simulate` to preview which workloads would be created without actually making API calls to the PCE.

## How It Works

1. Connects to the Illumio PCE using the provided API credentials.
2. Opens the FlowLink log file and watches for lines containing `"Following new IP addresses found in flows:"`.
3. Extracts IP addresses from matching log lines and checks if they fall within the configured networks.
4. For each matching IP, queries the PCE to see if a workload already exists.
5. If no workload exists, creates an unmanaged workload named `FlowLink-<IP>`.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
