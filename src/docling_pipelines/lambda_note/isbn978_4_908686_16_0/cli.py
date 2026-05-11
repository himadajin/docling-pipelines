from ...cli import run_book_cli
from .pipeline import PIPELINE


def main() -> None:
    run_book_cli(PIPELINE)
