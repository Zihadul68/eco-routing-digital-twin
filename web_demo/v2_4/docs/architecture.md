# System Architecture — Eco-Route Live V2.4

## 1. Technology Stack & Frameworks
- **Markup:** Semantic HTML5 (`<!DOCTYPE html>`, `<html lang="en" class="dark">`).
- **Styling:** Tailwind CSS v3 loaded via Play CDN (`https://cdn.tailwindcss.com`) with an inline `tailwind.config` script extending `Inter` (sans), `JetBrains Mono` (mono), and `slate.950` (`#070b14`), supplemented by an inline `<style>` block for custom range slider tracks/thumbs and `@keyframes pulse-border` throttling alerts.
- **Typography:** Google Fonts (`Inter` and `JetBrains Mono`).
- **Application Logic & Rendering:** Vanilla ES6+ JavaScript encapsulated inside an Immediately Invoked Function Expression (`(function () { ... })()`) to prevent global namespace pollution, paired with native HTML5 2D `<canvas>` rendering for real-time sparkline telemetry.
- **Backend / Storage / APIs:** **None.** The application is 100% client-side with zero backend services, zero databases, and zero external telemetry APIs. All state resides in volatile browser memory (`let state = { ... }`) and resets on page reload or clicking **Reset Cluster**.

## 2. Directory Structure
```text
eco-route-live-v2.4/
├── index.html                    # Complete self-contained application (HTML + CSS + JS)
├── README.md                     # Overview, simulation disclaimer, and quickstart
└── docs/
    ├── architecture.md           # Component and state architecture
    ├── simulation-methodology.md # Mathematical formulas, constants, and assumptions
    └── deployment-guide.md       # Local hosting and GitHub Pages deployment steps
```

## 3. Main Application Entry Point & Lifecycle
1. **`window.onload` Bootstrap:**
   - Calls `initRackCards()` to dynamically generate 6 DOM rack cards (`#rack-card-0` through `#rack-card-5`) inside `#racks-grid`, each containing a thermal glow backdrop (`#rack-glow-i`), status pill (`#rack-status-i`), 8 animated server blade LEDs (`#blade-i-0..7`), utilization bar (`#rack-load-bar-i`), and water draw readout (`#rack-water-i`).
   - Calls `setSchedulerMode('eco')` to initialize the active policy UI state.
   - Executes a **12-tick warm-up loop** (`for (let i = 0; i < 12; i++) tickSimulation();`) so thermal states stabilize and the 60-sample chart renders immediately on first paint.
   - Starts the main simulation heartbeat via `setInterval(tickSimulation, 800)` (1 simulation tick every `800 ms`).

## 4. Component & State Interaction
- **Central State Store (`state`):** Holds `mode` (`'eco'` or `'round-robin'`), `incomingRps` (`1800` default), `ambientTemp` (`31` default), `tick`, `racks` (active 6-rack array), `shadowRacks` (parallel Round-Robin 6-rack array), and `history` (`maxTemp[]` and `water[]` capped at 60 entries).
- **Simulation Tick Pipeline (`tickSimulation()`):**
  1. Increments `state.tick`.
  2. Advances the active cluster physics via `stepCluster(state.racks, state.mode, state.incomingRps, state.ambientTemp)`.
  3. Advances the invisible shadow baseline cluster in parallel via `stepCluster(state.shadowRacks, 'round-robin', state.incomingRps, state.ambientTemp)`.
  4. Passes both metric objects into `updateUI(activeMetrics, shadowMetrics)`, which updates the 4 top KPI cards, the Shadow Baseline Delta panel, all 6 rack cards, and invokes `drawTelemetryChart()`.
- **User Input Handlers:**
  - `#btn-eco-route` / `#btn-round-robin`: Mutate `state.mode` and toggle active Tailwind border/glow styling.
  - `#traffic-slider` (`200–4200`, step `50`) & `#ambient-slider` (`12–44`, step `1`): Update `state.incomingRps` and `state.ambientTemp` on `input` events.
  - `#spike-btn`: Sets `state.incomingRps = 3900` and syncs `#traffic-slider`.
  - `#reset-btn`: Deep-clones `INITIAL_RACKS` back into `state.racks` and `state.shadowRacks`, clears `state.history`, resets sliders to `1800 req/s` and `31°C`, and restores `'eco'` mode.