# product-reviews-provider-example

Example provider package for the `product-reviews` plugin system.

## Installation

```bash
pip install product-reviews-provider-example
```

## Usage

This package provides example provider:

1. **ExampleReviewsProvider** - for `example.com` URLs


## Structure

```
src/product_reviews_provider_example/
├── __init__.py
└── providers/
    ├── __init__.py
    └── example.py          # ExampleReviewsProvider
```

## Entry Points

The package registers providers via entry points:

```toml
[project.entry-points.'product_reviews.providers']
example = 'product_reviews_provider_example.providers.example:ExampleReviewsProvider'
```

This allows the `product-reviews` core to automatically discover and load these providers.
