"""
American Community Survey downloader (county-level) – first cut.
"""

from __future__ import annotations

import os
from typing import Sequence

import pandas as pd

from .cache import get as cached_get

_API = "https://api.census.gov/data/{year}/acs/acs5"
_KEY = os.getenv("CENSUS_API_KEY")  # optional


def get_county_table(
    year: int,
    variables: Sequence[str],
    *,
    state: str | None = None,
    ttl: str = "6h",
) -> pd.DataFrame:
    """
    Fetch *variables* for every county (or a single state) for *year*.

    Parameters
    ----------
    variables : list[str]
        e.g. ["B23025_004E", "B23025_003E"]  (Labour-force vars)
    state : "06" for CA, "01" for AL …  None = all states
    """
    vars_str = ",".join(["NAME", *variables])
    params = {"get": vars_str}

    if state:
        params["for"] = "county:*"
        params["in"] = f"state:{state}"
    else:
        params["for"] = "county:*"

    if _KEY:
        params["key"] = _KEY

    url = _API.format(year=year)
    resp = cached_get(url, params=params, ttl=ttl)
    resp.raise_for_status()

    data = resp.json()
    df = pd.DataFrame(data[1:], columns=data[0])
    df[variables] = df[variables].apply(pd.to_numeric, errors="coerce")
    # The API returns state and county as the last two columns
    df["geoid"] = df.iloc[:, -2] + df.iloc[:, -1]  # state + county
    return df
