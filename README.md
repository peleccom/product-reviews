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
