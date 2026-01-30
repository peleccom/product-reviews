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
