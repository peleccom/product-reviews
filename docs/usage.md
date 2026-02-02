# Usage

## CLI Usage

The `product-reviews` CLI provides three main commands:

### List available providers

List all available review providers and their information:

```bash
product-reviews list
```

### Scrape reviews from a URL

Extract reviews from a supported e-commerce URL:

```bash
product-reviews scrape <URL>
```

Example:
```bash
product-reviews scrape https://example.com/reviews/product-1
```

### Check provider health

Test the health and availability of providers:

```bash
# Check all providers
product-reviews health

# Check specific provider
product-reviews health --provider jsonfs
```

## Python API Usage

### Basic Usage

```python
from product_reviews import ProductReviewsService

# Initialize the service
service = ProductReviewsService()

# Parse reviews from a URL (using dummy provider for this example)
result = service.parse_reviews("https://example.com/reviews/product-1")

# Verify the result
assert result.provider == "dummy"
assert result.count() == 2
assert len(result.reviews) == 2

# Verify review properties
for review in result.reviews:
    assert review.rating is not None
    assert isinstance(review.rating, (int, float))
```

### Using Registry

The `Registry` class manages plugin loading and caching. You can use it directly or through `ProductReviewsService`:

```python
from product_reviews import Registry, ProductReviewsService
from pathlib import Path

# Create a registry with custom plugins directory
import os

registry = Registry(Path(os.getcwd()) / 'src/product_reviews/providers/providers')

# List all providers
providers = registry.list_providers()
print(f"Found {len(providers)} providers")

# Get provider for a specific URL
provider_class = registry.get_provider_for_url("https://example.com/reviews/product-1")

# Get provider by name
provider_class = registry.get_provider_class("JSON FS")
provider_instance = registry.get_provider("JSON FS")

# Iterate over all providers
for name, provider_class in registry.iter_providers():
    print(f"{name}: {provider_class}")

# Get provider names
names = registry.get_provider_names()
print(names)

# Clear cache to reload providers
registry.clear_cache()
```

### Using ProductReviewsService with Custom Registry

```python
from product_reviews import Registry, ProductReviewsService
from pathlib import Path

# Create a custom registry
registry = Registry()

# Pass to ProductReviewsService
service = ProductReviewsService(registry=registry)

# All service operations use the custom registry
result = service.parse_reviews("https://example.com/reviews/product-1")
providers = service.list_providers()
```

### Environment Variable Configuration

Set the plugins directory using an environment variable:

```bash
export PRODUCT_REVIEWS_PLUGINS_DIR=/path/to/your/plugins
```

Or programmatically:

```python fixture:clear_plugins_dir_env
import os
from product_reviews import get_plugins_dir

# Set the plugins directory via environment variable
os.environ['PRODUCT_REVIEWS_PLUGINS_DIR'] = '/path/to/your/plugins'

# Check the configured plugins directory
plugins_dir = get_plugins_dir()
assert plugins_dir is not None
print(f"Plugins directory: {plugins_dir}")
```

### List Available Providers

```python
from product_reviews import ProductReviewsService

service = ProductReviewsService()
# Get provider names
provider_names = service.get_provider_names()
assert isinstance(provider_names, list)
assert len(provider_names) >= 2  # At least JSON FS and dummy
assert "dummy" in provider_names
assert "JSON FS" in provider_names

# Get provider classes
provider_classes = service.list_providers()
assert isinstance(provider_classes, list)
assert len(provider_classes) >= 2

# Verify each provider has required attributes
for provider_class in provider_classes:
    provider = provider_class()
    assert hasattr(provider, "name")
    assert hasattr(provider, "description")
    assert provider.name in provider_names
```

### Get Specific Provider

```python
from product_reviews import ProductReviewsService

service = ProductReviewsService()

# Get provider by name
provider = service.get_provider("JSON FS")

# Check if URL matches provider
if provider.check_url("https://example.com/reviews/product-1"):
    reviews = provider.get_reviews("https://example.com/reviews/product-1")
```

### Working with Review Data

```python
from product_reviews.models import Review
from datetime import datetime

# Create a review directly
review = Review(
    rating=4.5,
    text="Great product!",
    created_at=datetime(2020, 1, 1, 12, 0, 0)
)

# Verify review properties
assert review.rating == 4.5
assert review.text == "Great product!"
assert review.created_at == datetime(2020, 1, 1, 12, 0, 0)

# Convert to dictionary
review_dict = review.to_dict()
assert review_dict["rating"] == 4.5
assert review_dict["text"] == "Great product!"
assert isinstance(review_dict["created_at"], datetime)

# Convert to JSON
review_json = review.to_json()
assert isinstance(review_json, str)
assert '"rating": 4.5' in review_json
assert '"text": "Great product!"' in review_json

# Create review from representation
review_data = {
    "rating": 4.5,
    "created_at": "2023-01-01T12:00:00",
    "text": "Great product!"
}
review2 = Review.from_representation(review_data)
assert review2.rating == 4.5
assert review2.text == "Great product!"
assert review2.created_at == datetime(2023, 1, 1, 12, 0, 0)
```

## Provider Development

### Creating a Custom Provider

Providers should inherit from `BaseReviewsProvider` and return `list[Review]` from `get_reviews`:

```python
from datetime import datetime
from typing import ClassVar
from product_reviews.models import Review
from product_reviews.providers.base import BaseReviewsProvider

class MyReviewsProvider(BaseReviewsProvider):
    name: ClassVar[str] = "my_provider"
    description: ClassVar[str] = "My custom reviews provider"
    url_regex: ClassVar[str] = r"https?://example\.com/.*"
    test_urls: ClassVar[list[str]] = [
        "https://example.com/product-1",
    ]

    def get_reviews(self, url: str) -> list[Review]:
        # Implement your review fetching logic here
        return [
            Review(
                rating=5.0,
                text="Excellent product!",
                created_at=datetime.now(),
            ),
            Review(
                rating=4.0,
                text="Good quality",
                created_at=datetime.now(),
            ),
        ]
```
