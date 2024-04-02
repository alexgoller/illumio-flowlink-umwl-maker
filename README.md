# Flowlink Unmanaged Workload Maker

Flowlink is the Illumio Core PCE Flow Collector. The flow collector sends flows
to the PCE and injects flows for workloads that are either managed or unmanaged
on the PCE.
This script automatically adds UMWL based on the home networks of the user.


## Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

## Installation

1. Navigate to the project directory:
    ```
    cd yourrepository
    ```
2. Install the required Python packages:
    ```
    pip install -r requirements.txt
    ```
3. Get API keys from PCE

Login to your PCE, create a service account or API key via user profile

4. Run program

## Usage

The script requires several command-line arguments or environment variables:

- `--pce_host` or `PCE_HOST`: The host of the PCE.
- `--pce_port` or `PCE_PORT`: The port of the PCE.
- `--org_id` or `ORG_ID`: The organization ID.
- `--api_user` or `PCE_API_USER`: The API user.
- `--api_key` or `PCE_API_KEY`: The API key.
- `--verbose`: Enable verbose logging.
- `--networks`: A comma-separated list of networks. (default: RFC1918 networks)
- `--simulate`: Simulate workload creation without actually creating workloads.

To run the script, use the following command:

  python flowlink-umwl-maker.py --pce_host your_pce_host --api_user your_api_user --api_key your_api_key --networks your_networks


Replace `your_pce_host`, `your_api_user`, `your_api_key`, and `your_networks` with your actual PCE host, API user, API key, and networks respectively.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.