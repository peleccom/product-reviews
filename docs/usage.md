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

# Parse reviews from a URL
reviews = service.parse_reviews("https://example.com/reviews/product-1")

print(f"Provider: {reviews.provider}")
print(f"Review count: {reviews.count()}")

# Access individual reviews
for review in reviews.reviews:
    print(f"Rating: {review.rating}")
    print(f"Text: {review.text}")
    print(f"Date: {review.created_at}")
```

### List Available Providers

```python
from product_reviews import ProductReviewsService

service = ProductReviewsService()

# Get provider names
providers = service.get_provider_names()
print(providers)

# Get provider classes
provider_classes = service.list_providers()
for provider_class in provider_classes:
    provider = provider_class()
    print(f"Name: {provider.name}")
    print(f"Description: {provider.description}")
```

### Get Specific Provider

```python
from product_reviews import ProductReviewsService

service = ProductReviewsService()

# Get provider by name
provider = service.get_provider("jsonfs")

# Check if URL matches provider
if provider.check_url("https://example.com/reviews/product-1"):
    reviews = provider.get_reviews("https://example.com/reviews/product-1")
```

### Working with Review Data

```python
from product_reviews import ProductReviewsService

service = ProductReviewsService()
reviews = service.parse_reviews("https://example.com/reviews/product-1ws")

# Convert to dictionary
for review in reviews.reviews:
    review_dict = review.to_dict()
    print(review_dict)

# Convert to JSON
for review in reviews.reviews:
    review_json = review.to_json()
    print(review_json)

# Create review from representation
from product_reviews import Review
review_data = {
    "rating": 4.5,
    "created_at": "2023-01-01T12:00:00",
    "text": "Great product!"
}
review = Review.from_representation(review_data)
```
