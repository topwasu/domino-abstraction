#!/usr/bin/env python3

import os
import sys


def main(scenario):
    scenario_name = os.path.basename(scenario).split(".")[0]
    pl_name = f"/tmp/dominos_{scenario_name}.pl"
    os.system(f"cat {scenario} dominos.pl > {pl_name}")

    actual = os.system(f"python3.11 dominos.py {scenario}")
    predicted = os.system(f"swipl -q -f {pl_name}")

    print(scenario, 1 if actual == 0 else 0, 1 if predicted == 0 else 0)


if __name__ == "__main__":
    if len(sys.argv) != 2:
        sys.exit("Usage: run_abstraction.py <file>")
    scenario = sys.argv[1]
    main(scenario)
