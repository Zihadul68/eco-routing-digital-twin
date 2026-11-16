# Simulation Methodology & Mathematical Formulas (V2.4)

> **Simulated vs. Empirical Data Notice:** All metrics computed in `stepCluster()` represent synthetic analytical approximations for comparative policy simulation. They are not real-world physical sensor readings or experimentally validated benchmarks.

## 1. Hardware Profiles & Rack Topology (`INITIAL_RACKS`)
The simulated data hall (`Data Hall A`) consists of $N = 6$ heterogeneous server racks with fixed physical parameters:

| Rack ID | Zone Description | Hardware Profile | Max Capacity ($R_{\max,i}$) | Airflow Factor ($\alpha_i$) | Thermal Mass ($\tau_i$) | Initial Temp ($T_{i,0}$) |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `RACK-01` | Cold Aisle West (CRAC-1) | `8× H100 SXM` | `850 req/s` | `1.22` | `0.16` | `36.0°C` |
| `RACK-02` | Mid Aisle West | `8× H100 SXM` | `850 req/s` | `1.05` | `0.15` | `39.0°C` |
| `RACK-03` | Inner Hot-Spot Core | `8× B200 HGX` | `950 req/s` | `0.76` | `0.13` | `45.0°C` |
| `RACK-04` | Inner Hot-Spot Core | `8× B200 HGX` | `950 req/s` | `0.79` | `0.13` | `44.0°C` |
| `RACK-05` | Mid Aisle East | `8× H100 SXM` | `850 req/s` | `1.08` | `0.15` | `38.5°C` |
| `RACK-06` | Cold Aisle East (CRAC-2) | `8× H100 SXM` | `850 req/s` | `1.25` | `0.16` | `35.5°C` |

- **Hardware Distinction:** `8× B200 HGX` racks (`RACK-03`, `RACK-04`) have higher peak inference throughput (`950 req/s` vs. `850 req/s`), but sit in the inner hot-aisle core with lower CRAC airflow factors (`0.76` and `0.79`) and lower thermal mass (`0.13`), causing faster temperature rise under uniform load.
- **Thermal Thresholds:** `THROTTLE_TEMP = 80.0°C`, `CRITICAL_TEMP = 85.0°C`.

## 2. Scheduling Algorithms
Each rack $i \in \{1..6\}$ receives a routing weight $w_i$ and traffic share $s_i = \frac{w_i}{\sum_{j=1}^{6} w_j}$, yielding assigned load $R_{\text{assigned},i} = R_{\text{total}} \cdot s_i$:

1. **Standard Round-Robin (`mode === 'round-robin'`):**
   $$w_i = 1 \implies s_i = \frac{1}{6} \approx 16.67\%$$
   Assumes uniform request distribution across all 6 racks regardless of thermal headroom or CRAC proximity.

2. **Thermal-Aware Eco-Routing (`mode === 'eco'`):**
   $$w_i = \max\left(0.05,\; \left(\frac{\max(2,\; (80.0 + 4) - T_i)}{40}\right)^{2.2} \cdot (\alpha_i)^{1.8}\right)$$
   - **Assumptions:** Combines a non-linear thermal headroom term (exponent `2.2` relative to an `84°C` soft ceiling) with a CRAC cooling-efficiency term (exponent `1.8` on `airflowFactor`). A floor of `0.05` prevents complete starvation of warm racks.

## 3. Thermal Throttling, Throughput & SLA Delivery
- **Effective Capacity ($R_{\text{eff},i}$):**
  - If $T_i < 80.0^\circ\text{C}$: $R_{\text{eff},i} = R_{\max,i}$ (`rack.throttled = false`).
  - If $T_i \ge 80.0^\circ\text{C}$:
    $$R_{\text{eff},i} = R_{\max,i} \cdot \max\left(0.45,\; 1 - (T_i - 80.0) \cdot 0.08\right)$$
    Derates GPU clock capacity by `8%` per degree above `80.0°C`, down to a `45%` minimum floor.
- **Delivered Throughput & Utilization:**
  $$R_{\text{actual},i} = \min(R_{\text{assigned},i},\; R_{\text{eff},i}), \quad U_i = \min\left(100,\; \frac{R_{\text{actual},i}}{R_{\max,i}} \cdot 100\right)$$
- **SLA Delivery Percentage:**
  $$\text{SLA\%} = \min\left(100,\; \frac{\sum_{i=1}^{6} R_{\text{actual},i}}{R_{\text{total}}} \cdot 100\right)$$
  *(Simulated capacity-delivery ratio; does not model tail latency or queuing delay).*

## 4. Rack Power & Thermodynamic Model
- **Rack IT Power ($P_{\text{IT},i}$, in kW):**
  $$P_{\text{IT},i} = 2.4 + \left(\frac{U_i}{100}\right) \cdot 9.6$$
  Assumes `2.4 kW` idle chassis draw plus up to `9.6 kW` dynamic GPU load (`12.0 kW` max per rack).
- **Equilibrium Target Temperature ($T_{\text{target},i}$, in °C):**
  $$T_{\text{target},i} = \min\left(89.0,\; (T_{\text{amb}} + 7.5) + \left(\frac{U_i}{100}\right) \cdot \frac{46.0}{\alpha_i}\right)$$
  Models a `7.5°C` cold-aisle delta above outdoor ambient $T_{\text{amb}}$ plus convective heat rise inversely proportional to CRAC airflow factor $\alpha_i$, capped at `CRITICAL_TEMP + 4` (`89.0°C`).
- **First-Order Thermal Inertia Update (per 800 ms tick):**
  $$T_i^{(t+1)} = T_i^{(t)} + \left(T_{\text{target},i} - T_i^{(t)}\right) \cdot \tau_i$$

## 5. Facility PUE & Evaporative Water Consumption (WUE Proxy)
- **Power Usage Effectiveness (PUE):**
  $$\text{PUE} = 1.09 + \max(0,\; T_{\text{amb}} - 15) \cdot 0.0045 + \max(0,\; T_{\max} - 55) \cdot 0.0032$$
  $$P_{\text{facility}} = \left(\sum_{i=1}^{6} P_{\text{IT},i}\right) \cdot \text{PUE}$$
- **Evaporative Cooling Water Draw ($W_i$, in Liters/hr):**
  $$M_{\text{amb}} = \max\left(0.25,\; 0.4 + \max(0,\; T_{\text{amb}} - 18) \cdot 0.055\right)$$
  $$M_{\text{hotspot},i} = \begin{cases} 1 + (T_i - 62) \cdot 0.045 & \text{if } T_i > 62^\circ\text{C} \\ 1.0 & \text{otherwise} \end{cases}$$
  $$W_i = \frac{P_{\text{IT},i} \cdot 2.15 \cdot M_{\text{amb}} \cdot M_{\text{hotspot},i}}{\sqrt{\alpha_i}}$$

## 6. Shadow Baseline & Historical Canvas Chart
- **Shadow Baseline:** `state.shadowRacks` runs `stepCluster(..., 'round-robin', ...)` every tick using identical `incomingRps` and `ambientTemp`. When `state.mode === 'eco'`, `Water Saved = max(0, shadowWater - activeWater)` and `Peak Temp Drop = max(0, shadowMaxTemp - activeMaxTemp)`.
- **Canvas Chart (`drawTelemetryChart()`):** Plots a rolling 60-tick buffer (`state.history.water` normalized against a fixed `0–600 L/hr` y-axis scale; `state.history.maxTemp` normalized against a `20–95°C` y-axis scale) with a dashed `80°C THROTTLE LIMIT` line.