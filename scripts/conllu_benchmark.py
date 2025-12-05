import argparse
import csv
from dataclasses import dataclass
from enum import auto, Enum
import gc
import hashlib
import io
import logging
from pathlib import Path
import sys
import time
from typing import Any, Callable

import conllu as alt

sys.path.insert(0, str(Path(__file__).parent.parent))

from pyconll.conllu import fast_conllu, conllu

logging.basicConfig(stream=sys.stdout, level=logging.INFO)


class ParserType(Enum):
    STANDARD = (auto(),)
    STANDARD_ITER = (auto(),)
    FAST = (auto(),)
    FAST_ITER = (auto(),)
    ALTERNATIVE = (auto(),)
    ALTERNATIVE_ITER = auto()


class MeasurementType(Enum):
    RUNTIME = auto()
    MEMORY = auto()


class ReportingUnit(Enum):
    RAW = auto()
    KB_PER = auto()
    PER_KB = auto()


@dataclass
class Args:
    corpora: Path
    parser: ParserType
    measurement: MeasurementType
    reporting_unit: ReportingUnit
    loops_per_file: int
    total_loops: int
    coverage: float
    output_csv: Path


EXCLUSIONS: dict[tuple[ParserType, MeasurementType], set[str]] = {
    (ParserType.FAST, MeasurementType.RUNTIME): {"cs_pdtc-ud-train"},
    (ParserType.FAST, MeasurementType.MEMORY): {"cs_pdtc-ud-train"},
}


def kernel(
    files: list[Path],
    loops_per_file: int,
    parser: Callable[[str], Any],
    measure: Callable[[str, Callable[[str], list]], float],
    coverage: float,
    exclusions: set[str],
) -> dict[Path, list[float]]:
    results: dict[Path, list[float]] = {}
    for file in files:
        hasher = hashlib.blake2b(str(file).encode(), digest_size=8)
        stamp = int.from_bytes(hasher.digest())
        if (stamp / ((1 << 64) - 1)) > coverage:
            logging.info("Skipping %s because it does not fall within the current coverage", file)
            continue

        if file.stem in exclusions:
            logging.info("Skipping %s because it is excluded for this parser.", file)
            results[file] = []
            continue

        text = file.read_text(encoding="utf-8")

        values: list[float] = []
        logging.info("Starting measurement loop for %s", file)
        for i in range(loops_per_file):
            logging.info("Starting iteration %d for %s", i + 1, file)
            value = measure(text, parser)
            gc.collect()
            values.append(value)

        logging.info("Finished measurements for %s", file)

        results[file] = values

    return results


def main(args: Args) -> None:
    if args.output_csv.exists():
        logging.error("The path %s already exists and will not be overwritten.", args.output_csv)
        return

    parser: Callable[[str], Any]
    if args.parser == ParserType.STANDARD:
        parser = lambda s: conllu.load_from_string(s)
    elif args.parser == ParserType.STANDARD_ITER:
        parser = lambda s: sum(len(sentence.tokens) for sentence in conllu.iter_from_string(s))
    elif args.parser == ParserType.FAST:
        parser = lambda s: fast_conllu.load_from_string(s)
    elif args.parser == ParserType.FAST_ITER:
        parser = lambda s: sum(len(sentence.tokens) for sentence in fast_conllu.iter_from_string(s))
    elif args.parser == ParserType.ALTERNATIVE:
        parser = lambda s: alt.parse(s)
    elif args.parser == ParserType.ALTERNATIVE_ITER:
        parser = lambda s: sum(len(tokenlist) for tokenlist in alt.parse_incr(io.StringIO(s)))
    else:
        raise RuntimeError(f"{args.parser} is not a properly handled format type.")

    measure: Callable[[str, Callable[[str], Any]], float]
    if args.measurement == MeasurementType.RUNTIME:

        def measure(text: str, parse: Callable[[str], list]) -> float:
            start = time.perf_counter()
            parsed = parse(text)
            end = time.perf_counter()

            del parsed

            return end - start

    elif args.measurement == MeasurementType.MEMORY:

        def measure(text: str, parse: Callable[[str], list]) -> float:
            from guppy import hpy

            hp = hpy()
            hp.setrelheap()
            corpus = parse(text)
            h = hp.heap()
            memory = h.size

            del h
            del corpus
            del hp
            del hpy

            return memory

    else:
        raise RuntimeError(f"{args.measurement} is not a properly handled measurement type.")

    convert: Callable[[Path, float], float]
    if args.reporting_unit == ReportingUnit.RAW:
        convert = lambda _, value: value
    elif args.reporting_unit == ReportingUnit.KB_PER:
        convert = lambda p, value: (p.stat().st_size / 1024) / value
    elif args.reporting_unit == ReportingUnit.PER_KB:
        convert = lambda p, value: value / (p.stat().st_size / 1024)
    else:
        raise RuntimeError(f"{args.reporting_unit} is not a properly handled reporting unit type.")

    files = sorted(args.corpora.glob("**/*.conllu"), key=lambda p: p.stat().st_size, reverse=True)
    results = kernel(
        files,
        args.loops_per_file,
        parser,
        measure,
        args.coverage,
        EXCLUSIONS.get((args.parser, args.measurement), set()),
    )

    with open(args.output_csv, "w", encoding="utf-8") as f:
        measurement_keys = [f"measurement_{i}" for i in range(args.loops_per_file)]
        writer = csv.DictWriter(f, ["key", "disk_kb", *measurement_keys])
        writer.writeheader()

        for conllu_file, values in sorted(results.items(), key=lambda p: p[0]):
            disk_kb = conllu_file.stat().st_size / 1024
            cols = {f"measurement_{i}": convert(conllu_file, v) for i, v in enumerate(values)}

            writer.writerow({"key": conllu_file.stem, "disk_kb": disk_kb, **cols})


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
        "--measurement",
        type=lambda s: MeasurementType[s],
        required=True,
        help="The type of measurement to make on the parsing.",
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
        "--reporting_unit",
        type=lambda s: ReportingUnit[s],
        required=True,
        help="The way to choose to display the measurement value in the final results.",
    )
    parser.add_argument(
        "--output_csv", type=Path, required=True, help="The location to write the csv output to."
    )

    args = parser.parse_args()

    main(
        Args(
            args.corpora,
            args.parser,
            args.measurement,
            args.reporting_unit,
            args.loops_per_file,
            args.total_loops,
            args.coverage,
            args.output_csv,
        )
    )
