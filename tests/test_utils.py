from product_reviews.utils import is_valid_url


def test_is_valid_url_with_valid_http():
    """Test is_valid_url returns True for valid HTTP URL."""
    assert is_valid_url("http://example.com")


def test_is_valid_url_with_valid_https():
    """Test is_valid_url returns True for valid HTTPS URL."""
    assert is_valid_url("https://example.com")


def test_is_valid_url_with_valid_subdomain():
    """Test is_valid_url returns True for valid subdomain URL."""
    assert is_valid_url("https://sub.example.com")


def test_is_valid_url_with_valid_path():
    """Test is_valid_url returns True for URL with path."""
    assert is_valid_url("https://example.com/path/to/resource")


def test_is_valid_url_with_valid_port():
    """Test is_valid_url returns True for URL with port."""
    assert is_valid_url("https://example.com:8080")


def test_is_valid_url_with_valid_query():
    """Test is_valid_url returns True for URL with query parameters."""
    assert is_valid_url("https://example.com?query=value")


def test_is_valid_url_with_invalid_scheme_ftp():
    """Test is_valid_url returns False for FTP scheme."""
    assert not is_valid_url("ftp://example.com")


def test_is_valid_url_with_invalid_scheme_missing():
    """Test is_valid_url returns False for missing scheme."""
    assert not is_valid_url("://example.com")


def test_is_valid_url_with_invalid_netloc_missing():
    """Test is_valid_url returns False for missing netloc."""
    assert not is_valid_url("https://")


def test_is_valid_url_with_empty_string():
    """Test is_valid_url returns False for empty string."""
    assert not is_valid_url("")


def test_is_valid_url_with_none():
    """Test is_valid_url returns False for None input."""
    # Function expects str, calling with None should return False
    assert not is_valid_url(None)  # type: ignore[arg-type]
