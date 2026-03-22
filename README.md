# test-cursor

Small utility script for fetching two Salesforce Account records.

## Usage

Set your Salesforce credentials:

```bash
export SALESFORCE_INSTANCE_URL="https://your-instance.my.salesforce.com"
export SALESFORCE_ACCESS_TOKEN="your-oauth-token"
```

Run the script:

```bash
python3 salesforce_fetch_accounts.py
```

Optional:

- `SALESFORCE_API_VERSION` to override the default API version (`v61.0`)
- `--instance-url`, `--access-token`, and `--api-version` CLI flags

## Tests

```bash
python3 -m unittest discover -s tests
```
