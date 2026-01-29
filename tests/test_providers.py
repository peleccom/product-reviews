import pytest

from product_reviews import NoMatchedProvidersException, ProductReviewsService


def test_unknown_url():
    """Test unknown URL raises NoMatchedProvidersException."""
    with pytest.raises(NoMatchedProvidersException):
        ProductReviewsService().parse_reviews("https://unknow.prover.domain/xxxx")
