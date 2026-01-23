import pytest

from product_reviews import NoMatchedProvidersException, ProductReviewsService


def test_unknown_url():
    with pytest.raises(NoMatchedProvidersException):
        ProductReviewsService().parse_reviews("https://unknow.prover.domain/xxxx")
