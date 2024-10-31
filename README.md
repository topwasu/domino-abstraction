# Domino Abstraction

`python run.py`

- To generate scenarios: `seq 0 35 | parallel --progress 'python3.11 dominos.py {} > scenarios/scenario{}.pl`
- To run abstraction on all scenarios, producing results: `gfind scenarios -type f -print0 | parallel --progress -0 'python run_abstraction.py' > results`
