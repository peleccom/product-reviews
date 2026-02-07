from abc import abstractmethod
from argparse import ArgumentParser, Namespace


class BaseCommand:
    name: str
    help: str

    @abstractmethod
    def add_arguments(self, parser: ArgumentParser):
        pass

    @abstractmethod
    def run(self, args: Namespace) -> int | None:
        pass
