# Domino Abstraction

`python run.py`

- `dominos.py` is used to generate scenarios
  - Considers different width/height ratios, numbers of dominos, and gaps in the domino sequence
- Abstraction uses `will-tip.py WIDTH HEIGHT` to determine whether a domino will tip if pushed.
  - All other reasoning is done without simulation.
- To generate scenarios: `seq 0 35 | parallel --progress 'python3.11 dominos.py {} > scenarios/scenario{}.pl`
- To run abstraction on all scenarios, producing results: `gfind scenarios -type f -print0 | parallel --progress -0 'python run_abstraction.py' > results`
