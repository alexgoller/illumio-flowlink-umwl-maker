# FlowLink Unmanaged Workload Maker

> Automatically create Unmanaged Workloads (UMWLs) on the Illumio PCE from IP addresses discovered in FlowLink logs.

FlowLink is the Illumio Core PCE Flow Collector. It sends network flows to the PCE for both managed and unmanaged workloads. This script **monitors FlowLink log files** in real time and automatically creates unmanaged workloads for new IP addresses found within your configured networks.

---

## Prerequisites

- **Python 3.6+**
- **Illumio PCE** with API access (service account or API key)

## Quick Start

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Run (with environment variables)
export PCE_HOST=pce.example.com
export PCE_API_USER=api_xxxxxxxxx
export PCE_API_KEY=your_api_secret

python flowlink-umwl-maker.py --log_file /var/log/flowlink.log
```

Or pass everything via flags:

```bash
python flowlink-umwl-maker.py \
  --pce_host pce.example.com \
  --api_user api_xxxxxxxxx \
  --api_key your_api_secret \
  --log_file /var/log/flowlink.log \
  --networks 10.0.0.0/8,172.16.0.0/12
```

---

## Configuration

All options can be set via **command-line flags** or **environment variables**.

### Connection

| Flag | Env Variable | Default | Description |
|:-----|:-------------|:--------|:------------|
| `--pce_host` | `PCE_HOST` | `poc1.illum.io` | PCE hostname |
| `--pce_port` | `PCE_PORT` | `443` | PCE TCP port |
| `--org_id` | `PCE_ORG` | `1` | Organization ID |
| `--api_user` | `PCE_API_USER` | **required** | API user / service account |
| `--api_key` | `PCE_API_KEY` | **required** | API key / secret |

### Behavior

| Flag | Default | Description |
|:-----|:--------|:------------|
| `--log_file` | **required** | Path to the FlowLink log file |
| `--networks` | `192.168.0.0/16,172.16.0.0/12,10.0.0.0/8` | Comma-separated list of internal networks |
| `--max-workloads` | `0` (unlimited) | Max workloads to create per batch of discovered IPs |
| `--simulate` | `false` | Preview workload creation without making API calls |
| `--notail` | `false` | Read the log file from the beginning instead of tailing |
| `--verbose` | `false` | Enable debug-level logging |

---

## How It Works

```
FlowLink Log ──> Script ──> Illumio PCE API
                   │
                   ├─ Parse IPs from log lines
                   ├─ Filter by configured networks
                   ├─ Check if workload exists on PCE
                   └─ Create UMWL if missing
```

1. Connects to the Illumio PCE and validates API credentials.
2. Opens the FlowLink log file and tails it for new entries (use `--notail` to read from the beginning).
3. Watches for lines containing **"Following new IP addresses found in flows:"**.
4. Extracts IP addresses and filters them against the configured `--networks`.
5. For each matching IP, checks the PCE for an existing workload.
6. If none exists, creates an unmanaged workload named **`FlowLink-<IP>`**.

The script runs continuously until stopped with `Ctrl+C`.

---

## Examples

**Dry run** -- see what would be created without touching the PCE:

```bash
python flowlink-umwl-maker.py \
  --log_file /var/log/flowlink.log \
  --simulate --notail --verbose
```

**Limit batch size** -- create at most 50 workloads per log line:

```bash
python flowlink-umwl-maker.py \
  --log_file /var/log/flowlink.log \
  --max-workloads 50
```

**Custom networks** -- only match IPs in specific subnets:

```bash
python flowlink-umwl-maker.py \
  --log_file /var/log/flowlink.log \
  --networks 10.1.0.0/16,10.2.0.0/16
```

---

## Security Notes

- **Prefer environment variables** for `PCE_API_USER` and `PCE_API_KEY`. Command-line flags are visible to other users on the system via `ps`.
- **Log file trust** — the script trusts the FlowLink log file contents. Ensure the log file has restrictive permissions so it cannot be written to by untrusted users.

---

## License

MIT
