# product-reviews

[![Release](https://img.shields.io/github/v/release/peleccom/product-reviews)](https://img.shields.io/github/v/release/peleccom/product-reviews)
[![Build status](https://img.shields.io/github/actions/workflow/status/peleccom/product-reviews/main.yml?branch=master)](https://github.com/peleccom/product-reviews/actions/workflows/main.yml?query=branch%3Amaster)
[![codecov](https://codecov.io/gh/peleccom/product-reviews/branch/master/graph/badge.svg)](https://codecov.io/gh/peleccom/product-reviews)
[![Commit activity](https://img.shields.io/github/commit-activity/m/peleccom/product-reviews)](https://img.shields.io/github/commit-activity/m/peleccom/product-reviews)
[![License](https://img.shields.io/github/license/peleccom/product-reviews)](https://img.shields.io/github/license/peleccom/product-reviews)

A plugin system for product reviews fetcher that allows collecting and analyzing customer reviews from various e-commerce platforms through extensible plugins.

## Installation

```bash
pip install product-reviews
```
or
```bash
uv add product-reviews
```

Or from source:

```bash
git clone https://github.com/peleccom/product-reviews
cd product-reviews
uv sync
```

## Usage

The CLI provides three main commands:

### List available providers
```bash
product-reviews list
```

### Scrape reviews from a URL
```bash
product-reviews scrape <URL>
```

### Check provider health
```bash
product-reviews health [--provider <provider_name>]
```

### Test providers
```bash
product-reviews test                    # Test all providers
product-reviews test --provider <name>  # Test specific provider
product-reviews test --re-record        # Clear mocks and re-record
```

## Pytest Plugin

The package includes a pytest plugin that **automatically generates tests** for all registered providers. No test files are required — tests are injected into the test suite at collection time.

### How it works

When `product-reviews` is installed, the plugin is automatically loaded by pytest via the `pytest11` entry point. It discovers all providers (built-in, filesystem, and entry point) and generates a test for each URL in `test_urls` and `invalid_urls`.

### Usage in a private provider project

1. Add `product-reviews` as a dependency of your provider package.
2. Record mock responses:
   ```bash
   product-reviews test --re-record
   ```
   This captures all HTTP requests/responses and saves them as YAML files in the provider's `mocks/` directory.
3. Run pytest:
   ```bash
   uv run pytest
   ```

The output will show auto-generated tests grouped under `product-reviews`:
```
tests/test_my_stuff.py ...                                               [ 60%]
product-reviews .....                                                    [100%]
```

With `-v` for details:
```
product-reviews::my_provider[https://example.com/reviews/1] PASSED
product-reviews::my_provider[https://example.com/reviews/2] PASSED
product-reviews::my_provider[invalid-https://example.com/bad] PASSED
```

### Test behavior

- **Valid URLs** (`test_urls`): Replays recorded HTTP mock data (stored in YAML format) and validates that the provider returns well-formed reviews. If no mock data has been recorded, the test **fails** with a message to run `product-reviews test --re-record`.
- **Invalid URLs** (`invalid_urls`): Replays recorded HTTP mock data and asserts that the provider raises `ReviewsParseException`. HTTP requests are also mocked for invalid URLs to ensure consistent, offline testing.

### Mock file format

Mock files are stored in YAML format for better readability and ease of manual editing:

```yaml
url: https://example.com/product
reviews:
  - author: John Doe
    rating: 5.0
    text: Great product!
captured_data:
  - method: GET
    url: https://example.com/api
    headers:
      Content-Type: application/json
    status_code: 200
    text: |
      {...}
```

## Python API

### Basic Usage

```python
from product_reviews import ProductReviewsService

service = ProductReviewsService()
reviews = service.parse_reviews("https://example.com/reviews/product-1")

print(f"Provider: {reviews.provider}")
print(f"Count: {reviews.count()}")
```

### Using Registry

```python
from product_reviews import Registry
from pathlib import Path

# Create registry with custom plugins directory
registry = Registry(plugins_dir=Path("/path/to/plugins"))

# List providers
providers = registry.list_providers()

# Get provider for URL
provider = registry.get_provider_for_url("https://example.com/reviews/product-1")

# Get provider by name
provider_class = registry.get_provider_class("jsonfs")
```

### Environment Variable

Set plugins directory via environment variable:

```bash
export PRODUCT_REVIEWS_PLUGINS_DIR=/path/to/plugins
```

```python
from product_reviews import get_plugins_dir

plugins_dir = get_plugins_dir()  # Returns Path or None
```
