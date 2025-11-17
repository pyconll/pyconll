import argparse
import csv
from dataclasses import dataclass
from enum import auto, Enum
from pathlib import Path
import sys
import time

sys.path.insert(0, str(Path(__file__).parent.parent))

from pyconll.conllu import compact_conllu, conllu, Token
from pyconll.format import Format

class FormatType(Enum):
    STANDARD = auto(),
    COMPACT = auto()

@dataclass
class Args:
    corpora: Path
    format: Format[Token]
    loops_per_file: int
    total_loops: int

@dataclass
class ConlluBenchmark:
    duration: int
    token_count: int
    memory: int

def kernel(files: list[Path], loops_per_file: int, format: Format[Token]) -> dict[str, ConlluBenchmark]:
    results = {}
    for file in files:
        duration = 0
        for _ in range(loops_per_file):
            start = time.perf_counter()
            corpus = format.load_from_file(file)
            end = time.perf_counter()

            duration += end - start

        corpus = format.iter_from_file(file)
        token_count = sum(len(sentence.tokens) for sentence in corpus)

        results[file.stem] = ConlluBenchmark(duration, token_count, 0)

    return results

def main(args: Args) -> None:
    if args.format == FormatType.STANDARD:
        format = conllu
    elif args.format == FormatType.COMPACT:
        format = compact_conllu
    else:
        raise RuntimeError(f"{args.format} is not a properly handled format type.")

    files = sorted(args.corpora.glob("**/*.conllu"))
    results = kernel(files, args.loops_per_file, format)

    writer = csv.DictWriter(sys.stdout, ["key", "tps", "kb"])
    writer.writeheader()

    for conllu_key, benchmark in sorted(results.items(), key=lambda p: p[0]):
        tps = (benchmark.token_count * args.loops_per_file) / benchmark.duration
        writer.writerow({"key": conllu_key, "tps": tps, "kb": (benchmark.memory / 1024)})

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpora", type=Path, required=True, help="The location from which to parse all CoNLL-U files.")
    parser.add_argument("--format", type=lambda s: FormatType[s], required=True, help="The type of CoNLL-U format provider to use.")
    parser.add_argument("--loops_per_file", type=int, required=True, help="The number of times to parse each file")
    parser.add_argument("--total_loops", type=int, required=True, help="The number of times to loop over all files.")

    args = parser.parse_args()

    main(Args(args.corpora, args.format, args.loops_per_file, args.total_loops))