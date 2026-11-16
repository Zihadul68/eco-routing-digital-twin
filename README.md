# Eco-Routing: Semantic Thermal Scheduling for LLM Data Centres

Research companion prototype for exploring semantic workload classification and spatially thermal-aware routing in a hypothetical multi-rack LLM inference cluster.

> **Research-status notice:** This repository contains illustrative simulations, not a validated data-centre digital twin. Rack temperatures, compute loads, cooling coefficients, PUE, and water-use outputs are model-generated estimates. They are not physical sensor readings or evidence of real-world energy or water savings. The V2.4 browser demo's water output is a modelled litres-per-hour proxy, not a validated Water Usage Effectiveness (WUE) measurement. Calibrate models with documented facility telemetry before making empirical claims.

## Interactive demos

### Eco-Route Live V2.4 — Thermal & Water-Aware AI Inference Scheduler

A richer, client-side dashboard with six heterogeneous simulated racks, H100/B200 labels, ambient-temperature and traffic controls, thermal-aware routing, a Round-Robin comparison baseline, and a rolling telemetry chart.

- **[Open V2.4 demo](web_demo/v2_4/index.html)**
- [V2.4 overview and quickstart](web_demo/v2_4/README.md)
- [System architecture](web_demo/v2_4/docs/architecture.md)
- [Simulation methodology and formulas](web_demo/v2_4/docs/simulation-methodology.md)
- [Deployment guide](web_demo/v2_4/docs/deployment-guide.md)

V2.4 is a browser-side illustrative model. It requires internet access to load Tailwind CSS and Google Fonts from their CDNs. It does not connect to physical equipment, sensors, facility APIs, or a backend.

### Original browser demo

The original, simpler six-rack browser demo is retained separately:

- **[Open original demo](web_demo/eco_route_live.html)**

## Python research prototype

The Python simulation explores semantic workload classification and spatially thermal-aware routing in a hypothetical multi-rack inference cluster.

- **Round-Robin baseline:** distributes requests evenly across racks.
- **Eco-routing prototype:** scores racks using current temperature, utilization, and a CRAC-proximity factor.
- **Thermal and water proxy:** evolves simplified rack temperatures and calculates an illustrative water-use proxy for comparative software experiments.

## Repository layout

```text
.
├── README.md
├── requirements.txt
├── eco_routing_twin.py
├── tests/
│   └── test_simulation.py
└── web_demo/
    ├── eco_route_live.html
    └── v2_4/
        ├── index.html
        ├── README.md
        └── docs/
            ├── architecture.md
            ├── simulation-methodology.md
            └── deployment-guide.md
```

## Python quickstart

Requires Python 3.9+; the simulation engine uses only the standard library.

```bash
python eco_routing_twin.py
```

Optional parameters:

```bash
python eco_routing_twin.py --steps 300 --rps 16 --ambient-c 36 --output results/simulation_results.csv
```

The CSV contains one time series for each scheduler mode. The `water_usage_lph_proxy` field is an illustrative proxy, not measured WUE.

## Run V2.4 locally

From the repository root:

```bash
python -m http.server 8080
```

Then open `http://localhost:8080/web_demo/v2_4/`. The page is static and has no backend, but internet access is needed for its CDN-hosted styling and fonts.

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
