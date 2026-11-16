# Eco-Route Live V2.4 — Thermal & Water-Aware AI Inference Cluster Scheduler

An interactive, client-side data center digital twin prototype simulating real-time thermal dynamics, GPU thermal throttling, Power Usage Effectiveness (PUE), and evaporative cooling tower water consumption (WUE) across heterogeneous AI inference racks.

## Disclaimer on Simulated Telemetry
All rack temperatures, power consumption figures, PUE ratios, evaporative water flow rates (`Liters/hr`), throughput values, and SLA percentages displayed in this prototype are **synthetic, model-generated estimates** produced by deterministic physics approximations inside the browser. They are intended for algorithmic visualization and comparative sensitivity analysis (`Standard Round-Robin` vs. `Thermal-Aware Eco-Routing`) and do not represent empirical physical sensor measurements.

## Features
- **6-Rack Heterogeneous Cluster Topology (`Data Hall A`):** Models 4× `8× H100 SXM` racks and 2× `8× B200 HGX` inner hot-spot racks with distinct CRAC airflow proximity factors (`0.76x` to `1.25x`) and thermal mass inertia (`0.13` to `0.16`).
- **Dual Routing Policy Engine:** Live switching between uniform `Standard Round-Robin` and `Thermal-Aware Eco-Routing` (weighted by thermal headroom below `80.0°C` and CRAC airflow efficiency).
- **Parallel Shadow Baseline:** Runs an invisible Round-Robin shadow cluster in lockstep to compute real-time water savings (`L/hr`) and peak temperature reductions (`°C`).
- **Interactive Stress Controls:** Real-time sliders for Incoming AI Inference Load (`200–4,200 req/s`) and Ambient Outdoor Temperature (`12°C–44°C`), plus a one-click `Simulate Traffic Burst` (`3,900 req/s`) trigger.
- **60-Tick Canvas Telemetry Chart:** HTML5 `<canvas>` trendline plotting Peak Rack Temperature (`°C`) against Evaporative Water Draw (`L/hr`) with an `80°C` throttle reference line.

## Quickstart
No build tools or package installation required:
1. Open `index.html` directly in any modern web browser, or serve locally via:
   ```bash
   python3 -m http.server 8080
   ```
2. Visit `http://localhost:8080` in your browser.

## Documentation
- [System Architecture](docs/architecture.md)
- [Simulation Methodology & Formulas](docs/simulation-methodology.md)
- [Independent Execution & Deployment Guide](docs/deployment-guide.md)