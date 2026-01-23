from urllib.parse import urlparse


def is_valid_url(url: str) -> bool:
    # Parse the URL
    parsed_url = urlparse(url)
    # Check if the scheme and netloc are valid (i.e., non-empty)
    return all([parsed_url.scheme in ["http", "https"], parsed_url.netloc])
