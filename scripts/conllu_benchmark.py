import argparse
import csv
from dataclasses import dataclass
from enum import auto, Enum
import logging
from pathlib import Path
import sys
import time
from typing import Callable

import conllu as alt
from guppy import hpy

sys.path.insert(0, str(Path(__file__).parent.parent))

from pyconll.conllu import compact_conllu, conllu, Token
from pyconll.format import Format

logging.basicConfig(level=logging.INFO)

EXCLUSION_NAMES: set[str] = {
    "cs_pdtc-ud-train.conllu",
    "de_hdt-ud-train.conllu",
    "ru_taiga-ud-train.conllu",
    "ru_syntagrus-ud-train.conllu",
}


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
    output_csv: Path


@dataclass
class ConlluBenchmark:
    duration: float
    file_size: int
    memory: int


def kernel(
    files: list[Path], loops_per_file: int, parser: Callable[[Path], list]
) -> dict[str, ConlluBenchmark]:
    results = {}
    for file in files:
        duration = 0.0
        logging.info("Starting runtime performance measuring loop for %s", file)
        for _ in range(loops_per_file):
            start = time.perf_counter()
            corpus = parser(file)
            end = time.perf_counter()

            duration += end - start

        logging.info("Starting memory usage measurment for %s", file)
        hp = hpy()
        hp.setrelheap()
        corpus = parser(file)
        h = hp.heap()

        logging.info("Finished measurements for %s", file)

        results[file.stem] = ConlluBenchmark(duration, file.stat().st_size, h.size)

    return results


def main(args: Args) -> None:
    parser: Callable[[Path], list]
    if args.parser == ParserType.STANDARD:
        parser = lambda p: conllu.load_from_file(p)
    elif args.parser == ParserType.COMPACT:
        parser = lambda p: compact_conllu.load_from_file(p)
    elif args.parser == ParserType.ALTERNATIVE:

        def parser(p):
            with open(p, encoding="utf-8") as f:
                text = f.read()
                return alt.parse(text)

    else:
        raise RuntimeError(f"{args.parser} is not a properly handled format type.")

    files = filter(lambda f: f.name not in EXCLUSION_NAMES, sorted(args.corpora.glob("**/*.conllu")))
    results = kernel(files, args.loops_per_file, parser)

    writer = csv.DictWriter(sys.stdout, ["key", "kbps", "in_memory_kb", "disk_kb"])
    writer.writeheader()

    for conllu_key, benchmark in sorted(results.items(), key=lambda p: p[0]):
        bps = (benchmark.file_size * args.loops_per_file) / benchmark.duration
        writer.writerow(
            {
                "key": conllu_key,
                "bps": bps / 1024,
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
        "--output_csv", type=Path, required=True, help="The location to write the csv output to."
    )

    args = parser.parse_args()

    main(Args(args.corpora, args.parser, args.loops_per_file, args.total_loops, args.output_csv))
