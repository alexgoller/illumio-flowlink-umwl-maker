# Flowlink Unmanaged Workload Maker

This script is used to create unmanaged workloads in Illumio's Policy Compute Engine (PCE) based on a list of IP addresses.

## Prerequisites

- Python 3.6 or higher
- pip (Python package installer)

## Installation

1. Clone the repository:
    ```
    git clone https://github.com/yourusername/yourrepository.git
    ```
2. Navigate to the project directory:
    ```
    cd yourrepository
    ```
3. Install the required Python packages:
    ```
    pip install -r requirements.txt
    ```

## Usage

The script requires several command-line arguments or environment variables:

- `--pce_host` or `PCE_HOST`: The host of the PCE.
- `--pce_port` or `PCE_PORT`: The port of the PCE.
- `--org_id` or `ORG_ID`: The organization ID.
- `--api_user` or `PCE_API_USER`: The API user.
- `--api_key` or `PCE_API_KEY`: The API key.
- `--verbose`: Enable verbose logging.
- `--networks`: A comma-separated list of networks.
- `--simulate`: Simulate workload creation without actually creating workloads.

To run the script, use the following command:

  python flowlink-umwl-maker.py --pce_host your_pce_host --api_user your_api_user --api_key your_api_key --networks your_networks


Replace `your_pce_host`, `your_api_user`, `your_api_key`, and `your_networks` with your actual PCE host, API user, API key, and networks respectively.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.