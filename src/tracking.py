"""
IncuBrix Tracking Module
Generates standardized UTM parameters and verifies destination URLs.
"""

from urllib.parse import urlencode, urlparse, parse_qs, urlunparse
from typing import Dict, Optional


def build_utm_url(
    destination_url: str,
    source: str,
    medium: str = "organic_social",
    campaign: str = "incubrix_growth_2027",
    content: str = "asset_001"
) -> str:
    """
    Constructs a verified destination URL with standard UTM tracking parameters.
    Ensures safe formatting and preserves any existing query parameters.
    """
    clean_dest = destination_url.strip()
    if not clean_dest.startswith("http://") and not clean_dest.startswith("https://"):
        clean_dest = f"https://{clean_dest}"

    parsed = urlparse(clean_dest)
    existing_params = parse_qs(parsed.query)

    # Standardize parameters
    params = {
        "utm_source": source.lower().replace(" ", "_"),
        "utm_medium": medium.lower().replace(" ", "_"),
        "utm_campaign": campaign.lower().replace(" ", "_"),
        "utm_content": content.lower().replace(" ", "_")
    }

    # Merge with existing query parameters
    for k, v in existing_params.items():
        if k not in params:
            params[k] = v[0] if isinstance(v, list) else v

    query_str = urlencode(params)
    new_parts = (parsed.scheme, parsed.netloc, parsed.path, parsed.params, query_str, parsed.fragment)
    return urlunparse(new_parts)


def validate_utm_url(url: str, required_keys: Optional[list] = None) -> Dict[str, any]:
    """
    Validates presence and validity of UTM parameters and destination host.
    """
    if required_keys is None:
        required_keys = ["utm_source", "utm_medium", "utm_campaign", "utm_content"]

    parsed = urlparse(url)
    if not parsed.scheme or not parsed.netloc:
        return {"valid": False, "reason": "Missing URL scheme (http/https) or host."}

    query_params = parse_qs(parsed.query)
    missing = [k for k in required_keys if k not in query_params or not query_params[k][0].strip()]

    if missing:
        return {"valid": False, "reason": f"Missing required UTM parameters: {', '.join(missing)}"}

    return {
        "valid": True,
        "scheme": parsed.scheme,
        "host": parsed.netloc,
        "params": {k: v[0] for k, v in query_params.items()}
    }
