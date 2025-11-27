import argparse
import csv
from dataclasses import dataclass
from enum import auto, Enum
import gc
import hashlib
import logging
import os
from pathlib import Path
import psutil
import sys
import time
from typing import Callable

import conllu as alt

sys.path.insert(0, str(Path(__file__).parent.parent))

from pyconll.conllu import compact_conllu, conllu, Token
from pyconll.format import Format

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class ParserType(Enum):
    STANDARD = (auto(),)
    COMPACT = (auto(),)
    ALTERNATIVE = auto()


@dataclass
class Args:
    corpora: Path
    parser: Format[Token]
    loops_per_file: int
    total_loops: int
    coverage: float
    output_csv: Path


@dataclass
class ConlluBenchmark:
    duration: float
    file_size: int
    memory: int


EXCLUSIONS_BY_PARSER: dict[ParserType, set[str]] = {
    ParserType.STANDARD: {"cs_pdtc-ud-train.conllu"}
}


def _get_current_memory_usage() -> int:
    p = psutil.Process(os.getpid())
    memory_info = p.memory_info()
    return memory_info.rss


def kernel(
    files: list[Path],
    loops_per_file: int,
    parser: Callable[[str], list],
    coverage: float,
    exclusions: set[str],
) -> dict[str, ConlluBenchmark]:
    results = {}
    for file in files:
        hasher = hashlib.blake2b(str(file).encode(), digest_size=8)
        stamp = int.from_bytes(hasher.digest())
        if (stamp / ((1 << 64) - 1)) > coverage:
            logging.info("Skipping %s because it does not fall within the current coverage", file)
            continue

        if file.name in exclusions:
            logging.info("Skipping %s because it is excluded for this parser.", file)
            results[file.stem] = ConlluBenchmark(-1, -1, -1)
            continue

        text = file.read_text(encoding="utf-8")

        duration = 0.0
        logging.info("Starting runtime performance measuring loop for %s", file)
        for i in range(loops_per_file):
            logging.info("Runtime performance measurement loop number %d for %s", i + 1, file)
            start = time.perf_counter()
            corpus = parser(text)
            end = time.perf_counter()

            del corpus
            gc.collect()

            duration += end - start

        logging.info("Starting memory usage measurement for %s", file)
        intial_rss_bytes = _get_current_memory_usage()
        corpus = parser(text)
        post_rss_bytes = _get_current_memory_usage()

        # Because parsing can be very high memory usage, make sure to cleanup all memory used
        # between invocations.
        del corpus
        del text
        gc.collect()

        logging.info("Finished measurements for %s", file)

        results[file.stem] = ConlluBenchmark(duration, file.stat().st_size * loops_per_file, post_rss_bytes - intial_rss_bytes)

    return results


def main(args: Args) -> None:
    parser: Callable[[str], list]
    if args.parser == ParserType.STANDARD:
        parser = lambda s: conllu.load_from_string(s)
    elif args.parser == ParserType.COMPACT:
        parser = lambda s: compact_conllu.load_from_string(s)
    elif args.parser == ParserType.ALTERNATIVE:
        parser = lambda s: alt.parse(s)
    else:
        raise RuntimeError(f"{args.parser} is not a properly handled format type.")

    files = sorted(args.corpora.glob("**/*.conllu"), key=lambda p: p.stat().st_size, reverse=True)
    results = kernel(
        files,
        args.loops_per_file,
        parser,
        args.coverage,
        EXCLUSIONS_BY_PARSER.get(args.parser, set()),
    )

    with open(args.output_csv, "w", encoding="utf-8") as f:
        writer = csv.DictWriter(f, ["key", "kbps", "in_memory_kb", "disk_kb"])
        writer.writeheader()

        for conllu_key, benchmark in sorted(results.items(), key=lambda p: p[0]):
            bps = benchmark.file_size / benchmark.duration
            writer.writerow(
                {
                    "key": conllu_key,
                    "kbps": bps / 1024,
                    "in_memory_kb": benchmark.memory / 1024,
                    "disk_kb": benchmark.file_size / 1024,
                }
            )


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--corpora",
        type=Path,
        required=True,
        help="The location from which to parse all CoNLL-U files.",
    )
    parser.add_argument(
        "--parser",
        type=lambda s: ParserType[s],
        required=True,
        help="The type of CoNLL-U parser to use.",
    )
    parser.add_argument(
        "--loops_per_file", type=int, required=True, help="The number of times to parse each file"
    )
    parser.add_argument(
        "--total_loops", type=int, required=True, help="The number of times to loop over all files."
    )
    parser.add_argument(
        "--coverage",
        type=float,
        required=False,
        default=1.0,
        help=(
            "Optional coverage from [0.0, 1.0] to represent how much of the corpus to cover. "
            "This uses hash based logic so that the files chosen are always the same, and also "
            "files included at lower coverage are included at higher coverage."
        ),
    )
    parser.add_argument(
        "--output_csv", type=Path, required=True, help="The location to write the csv output to."
    )

    args = parser.parse_args()

    main(
        Args(
            args.corpora,
            args.parser,
            args.loops_per_file,
            args.total_loops,
            args.coverage,
            args.output_csv,
        )
    )
