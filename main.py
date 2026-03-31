#!/usr/bin/env python3
"""Backward-compatible shim for the packaged CLI."""

from jv_link_raw_data_fetcher.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
