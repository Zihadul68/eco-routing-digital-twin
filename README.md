# Eco-Routing: Semantic Thermal Scheduling for LLM Data Centres

Research companion prototype for exploring semantic workload classification and spatially thermal-aware routing in a hypothetical multi-rack LLM inference cluster.

> **Research-status notice:** This repository is an illustrative simulation scaffold, not a validated data-centre digital twin. Rack temperatures, compute loads, CRAC proximity factors, cooling coefficients, and the water-use proxy are assumptions. The `water_usage_lph_proxy` output is **not** measured Water Usage Effectiveness (WUE), and must not be presented as measured facility consumption or as evidence of real-world savings. Calibrate the model with documented workload, rack, cooling, energy, and water telemetry before drawing empirical conclusions.

## Research concept

- **Semantic prompt classification:** represent lightweight chat and compute-intensive reasoning requests with different assumed compute loads and thermal weights.
- **Round-Robin baseline:** distribute requests cyclically without regard to rack state.
- **Eco-routing prototype:** score racks using current temperature, utilization, and a CRAC-proximity factor, then select the lowest-cost rack.
- **Thermal and water proxy:** evolve a simplified rack temperature state and calculate an illustrative water-use proxy for comparative software experiments.

## Repository layout

```text
.
├── README.md
├── requirements.txt
├── eco_routing_twin.py
├── tests/
│   └── test_simulation.py
└── web_demo/
    └── eco_route_live.html
```

## Quickstart

Requires Python 3.9+; the simulation engine uses only the standard library.

```bash
python eco_routing_twin.py
```

Optional parameters:

```bash
python eco_routing_twin.py --steps 300 --rps 16 --ambient-c 36 --output results/simulation_results.csv
```

The CSV contains one time series for each scheduler mode. The `water_usage_lph_proxy` field is explicitly a proxy, not a measured WUE value.

## Interactive browser demo

Open `web_demo/eco_route_live.html` in a modern browser. It runs locally and has no external dependencies. Change ambient temperature and traffic, inject a burst, and compare Round-Robin with the Eco-routing heuristic.

## Tests

```bash
python -m unittest discover -s tests -v
```

## Suggested research validation work

1. Replace synthetic request classes with a documented workload trace or a clearly specified reproducible generator.
2. Calibrate rack thermal dynamics against measured inlet/exhaust temperatures and cooling-system response.
3. Model facility water and energy from defensible equations and measured boundaries; report WUE/PUE definitions and units precisely.
4. Add repeated seeds, confidence intervals, parameter sensitivity, ablations (round-robin, thermal-only, semantic+thermal), and latency/SLA measurements.
5. Keep simulated results clearly separated from measured results in the paper and figures.

## Citation and attribution

Add the final paper citation, author list, DOI/preprint URL, and licence once those details are confirmed. No licence is asserted by this initial scaffold.
