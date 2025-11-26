import argparse
import csv
from dataclasses import dataclass
from enum import auto, Enum
from pathlib import Path
import sys
import time
from typing import Callable

import conllu as alt
from guppy import hpy

sys.path.insert(0, str(Path(__file__).parent.parent))

from pyconll.conllu import compact_conllu, conllu, Token
from pyconll.format import Format

hp = hpy()

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


@dataclass
class ConlluBenchmark:
    duration: int
    file_size: int
    memory: int


def kernel(
    files: list[Path], loops_per_file: int, parser: Callable[[Path], list]
) -> dict[str, ConlluBenchmark]:
    results = {}
    for file in files:
        duration = 0.0
        for _ in range(loops_per_file):
            start = time.perf_counter()
            corpus = parser(file)
            end = time.perf_counter()

            duration += end - start

        hp.setrelheap()
        corpus = parser(file)
        h = hp.heap()

        results[file.stem] = ConlluBenchmark(duration, file.stat().st_size, h.size)

    return results


def main(args: Args) -> None:
    parser: Callable[[Path], list]
    if args.format == ParserType.STANDARD:
        parser = lambda p: conllu.load_from_file(p)
    elif args.format == ParserType.COMPACT:
        parser = lambda p: compact_conllu.load_from_file(p)
    elif args.format == ParserType.ALTERNATIVE:

        def parser(p):
            with open(p, encoding="utf-8") as f:
                return alt.parse(f)

    else:
        raise RuntimeError(f"{args.parser} is not a properly handled format type.")

    files = sorted(args.corpora.glob("**/*.conllu"))
    results = kernel(files, args.loops_per_file, parser)

    writer = csv.DictWriter(sys.stdout, ["key", "bps", "kb"])
    writer.writeheader()

    for conllu_key, benchmark in sorted(results.items(), key=lambda p: p[0]):
        bps = (benchmark.file_size * args.loops_per_file) / benchmark.duration
        writer.writerow({"key": conllu_key, "bps": bps, "kb": benchmark.memory / 1024})


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

    args = parser.parse_args()

    main(Args(args.corpora, args.parser, args.loops_per_file, args.total_loops))
