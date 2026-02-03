import logging
from collections.abc import Generator
from importlib import util as importlib_util
from pathlib import Path

from .base import BaseReviewsProvider

logger = logging.getLogger(__name__)

PROVIDERS_DIR = Path(__file__).parent / "providers"


def get_local_providers_dir() -> Path:
    return PROVIDERS_DIR


def load_fs_provider(provider_path: Path) -> type[BaseReviewsProvider] | None:
    if not provider_path.is_dir():
        return None

    provider_file = provider_path / "provider.py"
    if not provider_file.exists():
        logger.debug(f"No provider.py found in {provider_path}")
        return None

    try:
        spec = importlib_util.spec_from_file_location(provider_path.name, provider_file)
        if spec is None or spec.loader is None:
            return None

        module = importlib_util.module_from_spec(spec)
        spec.loader.exec_module(module)

        provider_class = _find_provider_in_module(module)
        if provider_class is None:
            logger.warning(f"No provider class found in {provider_file}")
            return None

        if not isinstance(provider_class, type) or not issubclass(provider_class, BaseReviewsProvider):
            logger.warning(f"Provider in {provider_file} does not subclass BaseReviewsProvider")
            return None

        logger.debug(f"Loaded provider {provider_class.name!r} from {provider_path}")
        return provider_class  # noqa: TRY300
    except Exception as e:
        logger.warning(f"Failed to load provider from {provider_path}: {e}", exc_info=True)
        return None


def _find_provider_in_module(module: object) -> type[BaseReviewsProvider] | None:
    provider_class = getattr(module, "provider", None)
    if provider_class is not None:
        return provider_class

    module_name = getattr(module, "__name__", "").split(".")[-1] or ""
    if module_name:
        provider_class = getattr(module, f"{module_name.title()}Provider", None)
        if provider_class is not None:
            return provider_class

    for attr in dir(module):
        obj = getattr(module, attr)
        if isinstance(obj, type) and issubclass(obj, BaseReviewsProvider) and obj is not BaseReviewsProvider:
            return obj
    return None


def load_fs_providers(
    providers_dir: Path | None = None,
) -> Generator[type[BaseReviewsProvider], None, None]:
    if providers_dir is None:
        providers_dir = get_local_providers_dir()

    if not providers_dir.is_dir():
        logger.debug(f"Providers directory not found: {providers_dir}")
        return

    for provider_path in providers_dir.iterdir():
        if not provider_path.is_dir():
            continue

        if provider_path.name.startswith("_") or provider_path.name.startswith("."):
            continue

        provider_class = load_fs_provider(provider_path)
        if provider_class is not None:
            yield provider_class
