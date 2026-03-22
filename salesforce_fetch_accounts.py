#!/usr/bin/env python3
"""Fetch two Salesforce Account records with the REST API."""

from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any


DEFAULT_API_VERSION = "v61.0"
DEFAULT_FIELDS = ("Id", "Name")


def build_query(limit: int = 2, fields: tuple[str, ...] = DEFAULT_FIELDS) -> str:
    """Build a SOQL query for Salesforce Account records."""
    selected_fields = ", ".join(fields)
    return f"SELECT {selected_fields} FROM Account LIMIT {limit}"


def fetch_accounts(
    instance_url: str,
    access_token: str,
    *,
    api_version: str = DEFAULT_API_VERSION,
    limit: int = 2,
    fields: tuple[str, ...] = DEFAULT_FIELDS,
) -> dict[str, Any]:
    """Query Salesforce for Account records."""
    query = build_query(limit=limit, fields=fields)
    encoded_query = urllib.parse.urlencode({"q": query})
    url = f"{instance_url.rstrip('/')}/services/data/{api_version}/query?{encoded_query}"
    request = urllib.request.Request(
        url,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        },
    )

    with urllib.request.urlopen(request) as response:
        payload = response.read().decode("utf-8")
        return json.loads(payload)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Fetch two Account records from Salesforce.",
    )
    parser.add_argument(
        "--instance-url",
        default=os.environ.get("SALESFORCE_INSTANCE_URL"),
        help="Salesforce instance URL. Defaults to SALESFORCE_INSTANCE_URL.",
    )
    parser.add_argument(
        "--access-token",
        default=os.environ.get("SALESFORCE_ACCESS_TOKEN"),
        help="Salesforce OAuth access token. Defaults to SALESFORCE_ACCESS_TOKEN.",
    )
    parser.add_argument(
        "--api-version",
        default=os.environ.get("SALESFORCE_API_VERSION", DEFAULT_API_VERSION),
        help=f"Salesforce REST API version. Defaults to {DEFAULT_API_VERSION}.",
    )
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    if not args.instance_url or not args.access_token:
        print(
            "Both Salesforce instance URL and access token are required.",
            file=sys.stderr,
        )
        return 1

    try:
        response = fetch_accounts(
            args.instance_url,
            args.access_token,
            api_version=args.api_version,
        )
    except urllib.error.HTTPError as exc:
        message = exc.read().decode("utf-8", errors="replace")
        print(f"Salesforce request failed: {exc.code} {message}", file=sys.stderr)
        return 1
    except urllib.error.URLError as exc:
        print(f"Salesforce connection failed: {exc.reason}", file=sys.stderr)
        return 1

    records = response.get("records", [])
    print(json.dumps(records[:2], indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
