"""Illustrative digital-twin prototype for semantic, thermal-aware LLM workload routing.

This is a research prototype, not a calibrated data-centre model. Thermal and water
coefficients are explicit assumptions that must be replaced/calibrated with measured
facility telemetry before making empirical claims.
"""
from __future__ import annotations

import argparse
import csv
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List


@dataclass
class ServerRack:
    rack_id: str
    crac_proximity_factor: float
    current_temp_c: float
    utilization: float = 0.05
    throttled_requests: int = 0

    def update_thermal_state(self, ambient_c: float, dt_sec: float = 5.0) -> None:
        # Simplified first-order heat/cooling model; coefficients are assumptions.
        heat_gain = self.utilization * 18.5 * (dt_sec / 60.0)
        target_c = ambient_c - 4.0
        cooling = 0.35 * self.crac_proximity_factor * (self.current_temp_c - target_c) * (dt_sec / 60.0)
        self.current_temp_c = max(ambient_c - 2.0, self.current_temp_c + heat_gain - cooling)


@dataclass(frozen=True)
class LLMRequest:
    request_id: int
    prompt_type: str
    compute_load: float
    thermal_weight: float


class EcoRoutingDigitalTwin:
    PROXIMITIES = (1.0, 0.95, 0.62, 0.60, 0.92, 1.0)

    def __init__(self, num_racks: int = 6, ambient_temp_c: float = 36.0, seed: int = 42):
        if num_racks < 1:
            raise ValueError("num_racks must be at least 1")
        self.ambient_temp_c = float(ambient_temp_c)
        self.rng = random.Random(seed)
        self.racks = [
            ServerRack(f"RACK-{i + 1:02d}", self.PROXIMITIES[i % len(self.PROXIMITIES)], ambient_temp_c - 4.0)
            for i in range(num_racks)
        ]
        self.rr_pointer = 0

    def classify_prompt(self, req_id: int) -> LLMRequest:
        if self.rng.random() < 0.70:
            return LLMRequest(req_id, "lightweight_chat", 0.08, 1.0)
        return LLMRequest(req_id, "heavy_reasoning", 0.26, 2.4)

    def route_round_robin(self, req: LLMRequest) -> ServerRack:
        rack = self.racks[self.rr_pointer % len(self.racks)]
        self.rr_pointer += 1
        return rack

    def route_eco_semantic(self, req: LLMRequest) -> ServerRack:
        def cost(rack: ServerRack) -> float:
            thermal_penalty = math.exp(max(0.0, (rack.current_temp_c - 65.0) / 8.0))
            load_penalty = rack.utilization * 15.0
            airflow_penalty = (1.0 - rack.crac_proximity_factor) * 12.0 * req.thermal_weight
            # Semantic weight modestly increases sensitivity to the rack's thermal state.
            return thermal_penalty * req.thermal_weight + load_penalty + airflow_penalty
        return min(self.racks, key=cost)

    def estimate_water_liters_per_hr(self) -> float:
        """Illustrative proxy only; not a standards-compliant measured WUE calculation."""
        total_it_kw = sum(0.8 + rack.utilization * 4.2 for rack in self.racks)
        peak_temp = max(r.current_temp_c for r in self.racks)
        ambient_factor = 1.0 + max(0.0, self.ambient_temp_c - 25.0) * 0.045
        hotspot_factor = 1.0 + max(0.0, peak_temp - 70.0) ** 1.35 * 0.06
        proxy_l_per_kwh = 1.45 * ambient_factor * hotspot_factor
        return total_it_kw * proxy_l_per_kwh

    def run_simulation(self, steps: int = 300, rps: int = 16, mode: str = "eco") -> List[Dict[str, float | int | str]]:
        if steps < 1 or rps < 0:
            raise ValueError("steps must be positive and rps cannot be negative")
        if mode not in {"eco", "round_robin"}:
            raise ValueError("mode must be 'eco' or 'round_robin'")
        telemetry: List[Dict[str, float | int | str]] = []
        throttled_total = 0
        req_counter = 0
        for step in range(steps):
            for rack in self.racks:
                rack.utilization = max(0.05, rack.utilization * 0.72)
            active_rps = rps * 2 if 100 <= step <= 180 else rps
            for _ in range(active_rps):
                req_counter += 1
                req = self.classify_prompt(req_counter)
                target = self.route_eco_semantic(req) if mode == "eco" else self.route_round_robin(req)
                target.utilization = min(1.0, target.utilization + req.compute_load)
                if target.current_temp_c >= 80.0:
                    target.throttled_requests += 1
                    throttled_total += 1
            for rack in self.racks:
                rack.update_thermal_state(self.ambient_temp_c)
            temps = [r.current_temp_c for r in self.racks]
            telemetry.append({
                "step": step, "mode": mode, "ambient_c": self.ambient_temp_c,
                "active_rps": active_rps,
                "avg_rack_temp_c": round(sum(temps) / len(temps), 2),
                "peak_rack_temp_c": round(max(temps), 2),
                "water_usage_lph_proxy": round(self.estimate_water_liters_per_hr(), 2),
                "cumulative_sla_throttles": throttled_total,
            })
        return telemetry


def run_benchmark(steps: int, rps: int, ambient_c: float, output: Path) -> None:
    rr = EcoRoutingDigitalTwin(ambient_temp_c=ambient_c, seed=42).run_simulation(steps, rps, "round_robin")
    eco = EcoRoutingDigitalTwin(ambient_temp_c=ambient_c, seed=42).run_simulation(steps, rps, "eco")
    output.parent.mkdir(parents=True, exist_ok=True)
    with output.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rr[0].keys()))
        writer.writeheader()
        writer.writerows(rr + eco)
    rr_water = sum(float(row["water_usage_lph_proxy"]) for row in rr) / len(rr)
    eco_water = sum(float(row["water_usage_lph_proxy"]) for row in eco) / len(eco)
    saving = ((rr_water - eco_water) / rr_water * 100.0) if rr_water else 0.0
    print(f"Round-Robin mean water proxy: {rr_water:.2f} L/hr | peak: {max(float(x['peak_rack_temp_c']) for x in rr):.2f} C | throttles: {rr[-1]['cumulative_sla_throttles']}")
    print(f"Eco-routing mean water proxy: {eco_water:.2f} L/hr | peak: {max(float(x['peak_rack_temp_c']) for x in eco):.2f} C | throttles: {eco[-1]['cumulative_sla_throttles']}")
    print(f"Relative water-proxy difference: {saving:.2f}% (positive means lower under eco-routing)")
    print(f"Wrote {output}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--steps", type=int, default=300)
    parser.add_argument("--rps", type=int, default=16)
    parser.add_argument("--ambient-c", type=float, default=36.0)
    parser.add_argument("--output", type=Path, default=Path("simulation_results.csv"))
    args = parser.parse_args()
    run_benchmark(args.steps, args.rps, args.ambient_c, args.output)
