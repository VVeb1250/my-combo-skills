"""Independent phase-specific oracle. Keep outside the model's fixture.

Usage: python commander_oracle.py /path/to/fixture baseline|smoke|threshold
No model calls, does not write fixture files. Only use with trusted synthetic code.
"""
from pathlib import Path
import sys


def check(root: Path, phase: str) -> list[str]:
    # Each evaluation runs in a fresh process (avoid importing another arm's code).
    sys.path.insert(0, str(root.resolve()))
    from src.arbitration import decide
    threshold = 80 if phase == 'threshold' else 70
    smoke_exception = phase != 'baseline'
    failures = []
    for order in ('hold', 'move', 'free'):
        for risk in (0, 69, 70, 79, 80, 100):
            for smoke in (False, True):
                for loaded in (False, True):
                    if order == 'hold':
                        expected = ('hold', loaded)
                    elif order == 'move':
                        expected = ('advance', loaded)
                    elif risk >= threshold:
                        expected = ('retreat', smoke_exception and smoke and loaded)
                    else:
                        expected = ('hold', loaded)
                    got = decide(order, risk, smoke, loaded)
                    if (got.movement, got.fire) != expected:
                        failures.append(f'{order=}, {risk=}, {smoke=}, {loaded=}: {got!r} != {expected}')
    return failures


if __name__ == '__main__':
    if len(sys.argv) != 3 or sys.argv[2] not in ('baseline', 'smoke', 'threshold'):
        raise SystemExit(__doc__)
    failures = check(Path(sys.argv[1]), sys.argv[2])
    print('\n'.join(failures) if failures else 'PASS: 72 independent scenarios')
    raise SystemExit(bool(failures))
