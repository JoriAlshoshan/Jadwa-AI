import re

def _clean_part(x):
    if not x:
        return ""
    x = str(x).strip()
    x = re.sub(r"\s+", " ", x)
    x = x.strip(" ,-|–—")
    return x

def format_location(city=None, region=None, country="Saudi Arabia"):
    city = _clean_part(city)
    region = _clean_part(region)
    country = _clean_part(country) or "Saudi Arabia"

    parts = []
    for p in [city, region, country]:
        if not p:
            continue
        if not any(p.lower() == existing.lower() for existing in parts):
            parts.append(p)

    return " • ".join(parts) if parts else country