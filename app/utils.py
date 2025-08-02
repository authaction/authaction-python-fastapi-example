
import os

def url(path: str) -> str:
    domain = os.getenv("AUTHACTION_DOMAIN")
    return f"https://{domain}{path}"