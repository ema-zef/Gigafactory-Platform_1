import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import {
  ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  Legend, PieChart, Pie, Cell
} from "recharts";

const API = import.meta.env.VITE_API_URL || "http://localhost:8000";

const COLORS = ["#2563eb", "#f59e0b", "#10b981", "#ef4444", "#8b5cf6", "#06b6d4", "#ec4899", "#84cc16"];
const COST_COLORS = ["#2563eb", "#f59e0b"];
const ENERGY_COLORS = ["#06b6d4", "#f97316"];

const firstNumber = (obj, keys, fallback = 0) => {
  for (const key of keys) {
    const value = obj?.[key];
    if (value !== undefined && value !== null && value !== "" && Number.isFinite(Number(value))) {
      return Number(value);
    }
  }
  return Number(fallback) || 0;
};

const fmt = (value, digits = 0) =>
  Number(value ?? 0).toLocaleString(undefined, { maximumFractionDigits: digits });

const compact = value =>
  Number(value ?? 0).toLocaleString(undefined, { notation: "compact", maximumFractionDigits: 1 });

function metric(result, path, fallback = 0) {
  return path.reduce((value, key) => value?.[key], result) ?? fallback;
}

export default function Analytics() {
  const [scenarios, setScenarios] = useState([]);
  const [selectedId, setSelectedId] = useState("");
  const [scenario, setScenario] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    loadScenarios();
  }, []);

  async function loadScenarios() {
    try {
      setLoading(true);
      setError("");
      const { data } = await axios.get(`${API}/scenarios`);
      const rows = Array.isArray(data) ? data : [];
      setScenarios(rows);
      if (rows.length) {
        const id = rows[0].scenario_id;
        setSelectedId(String(id));
        await loadScenario(id);
      }
    } catch (err) {
      setError(err.response?.data?.detail || "Unable to load analytics.");
    } finally {
      setLoading(false);
    }
  }

  async function loadScenario(id) {
    if (!id) return;
    try {
      setError("");
      const { data } = await axios.get(`${API}/scenarios/${id}`);
      setScenario(data);
    } catch (err) {
      setScenario(null);
      setError(err.response?.data?.detail || "Unable to load scenario.");
    }
  }

  async function handleScenarioChange(event) {
    const id = event.target.value;
    setSelectedId(id);
    await loadScenario(id);
  }

  const result = scenario?.result_json || scenario?.result || {};

  const analytics = useMemo(() => {
    const technologies =
      Array.isArray(result?.technologies) ? result.technologies :
      Array.isArray(result?.technology_results) ? result.technology_results :
      Array.isArray(result?.results_by_technology) ? result.results_by_technology : [];
    const materialRequirements =
      result?.material_requirements && typeof result.material_requirements === "object"
        ? Object.entries(result.material_requirements).map(([name, value]) => ({
            name: name.replaceAll("_", " "),
            value: Number(value) || 0,
          }))
        : [];

    const operating = Number(metric(result, ["overall", "costs", "operating", "total"],
      metric(result, ["costs", "operating", "total"], 0)));
    const materials = Number(metric(result, ["overall", "costs", "materials", "total"],
      metric(result, ["costs", "materials", "total"], 0)));
    const totalCost = Number(metric(result, ["overall", "costs", "total"], operating + materials));

    const electricity = Number(metric(result, ["overall", "energy", "electricity"],
      metric(result, ["energy", "electricity"], 0)));
    const gas = Number(metric(result, ["overall", "energy", "gas"],
      metric(result, ["energy", "gas"], 0)));
    const totalEnergy = Number(metric(result, ["overall", "energy", "total"],
      metric(result, ["energy", "total"], electricity + gas)));

    const techRows = technologies.map((t, index) => ({
      name: t.technology_name || t.technology || t.name || `Step ${index + 1}`,
      process: t.process || t.process_name || "",
      branch: String(t.branch || t.electrode || t.process_category || t.route || "Other").toLowerCase(),
      environment: t.environment || "none",
      machines: firstNumber(t?.machines, ["machines"], firstNumber(t, ["machine_count", "number_of_machines", "required_machines"])),
      operators: firstNumber(t?.operators, ["operators_max", "operators_min"], firstNumber(t, ["operator_count", "number_of_operators", "required_operators"])),
      energy: firstNumber(t?.energy, ["total"], firstNumber(t, ["total_energy", "energy_total", "total_energy_kwh"])),
      cost: firstNumber(t?.costs, ["total", "direct_operating"], firstNumber(t, ["total_cost", "operating_cost", "cost_total"])),
      carbon: firstNumber(t?.carbon, ["total"], firstNumber(t, ["total_carbon", "carbon_emissions", "co2", "co2e"])),
      dryRoomEnergy: Number(t?.environment_allocation?.energy?.total || 0),
      dryRoomCost: Number(t?.environment_allocation?.costs?.total || 0),
      dryRoomCarbon: Number(t?.environment_allocation?.carbon?.total || 0),
    })).map(row => {
      const totalEnergy = row.energy + row.dryRoomEnergy;
      const totalCost = row.cost + row.dryRoomCost;
      const totalCarbon = row.carbon + row.dryRoomCarbon;
      return {
        ...row,
        totalEnergy,
        totalCost,
        totalCarbon,
        dryRoomEnergyShare: totalEnergy > 0 ? (row.dryRoomEnergy / totalEnergy) * 100 : 0,
        dryRoomCostShare: totalCost > 0 ? (row.dryRoomCost / totalCost) * 100 : 0,
        dryRoomCarbonShare: totalCarbon > 0 ? (row.dryRoomCarbon / totalCarbon) * 100 : 0,
      };
    });

    const top = (key, count = 8) =>
      techRows.slice().sort((a, b) => b[key] - a[key]).slice(0, count);

    const branchMap = {};
    techRows.forEach(row => {
      const branch = row.branch || "Other";
      branchMap[branch] ||= { branch, machines: 0, operators: 0, energy: 0, cost: 0, carbon: 0 };
      ["machines", "operators", "energy", "cost", "carbon"].forEach(k => {
        branchMap[branch][k] += row[k];
      });
    });

    const operatingCosts = result?.overall?.costs?.operating || {};
    const materialCosts = result?.overall?.costs?.materials || {};
    const annualEnergyKwh = Number(result?.capacity?.annual_energy_kwh || 0);
    const cellsDay = Number(result?.capacity?.required_good_cells_day || 0);

    const operatingBreakdown = [
      { name: "Labour", value: Number(operatingCosts.labour || 0) },
      { name: "Electricity", value: Number(operatingCosts.electricity || 0) },
      { name: "Gas", value: Number(operatingCosts.gas || 0) },
      { name: "Overhead", value: Number(operatingCosts.overhead || 0) },
      { name: "Floor space", value: Number(operatingCosts.floor_space || 0) },
    ].filter(x => x.value > 0);

    const materialComponentKeys = Array.from(new Set(
      ["cathode", "anode", "assembly"].flatMap(branch => {
        const group = materialCosts?.[branch] || {};
        return Object.keys(group).filter(name => name !== "total" && !name.includes("_kg") && !name.includes("trim_purchase") && Number(group[name]) > 0);
      })
    ));
    const materialCostByBranch = ["cathode", "anode", "assembly"].map(branch => {
      const group = materialCosts?.[branch] || {};
      const row = { name: branch };
      materialComponentKeys.forEach(key => { row[key] = Number(group[key] || 0); });
      return row;
    }).filter(row => materialComponentKeys.some(key => row[key] > 0));

    const branchEnergyMap = {};
    techRows.forEach(row => {
      const original = technologies.find(t => (t.technology_name || t.technology || t.name) === row.name) || {};
      const branch = row.branch || "other";
      branchEnergyMap[branch] ||= { branch, electricity: 0, gas: 0, total: 0 };
      branchEnergyMap[branch].electricity += Number(original?.energy?.electricity || 0);
      branchEnergyMap[branch].gas += Number(original?.energy?.gas || 0);
      branchEnergyMap[branch].total += Number(original?.energy?.total || 0);
    });

    const qualityFlow = technologies.map((t, index) => ({
      name: t.technology_name || `Step ${index + 1}`,
      branch: t.branch || "other",
      quality: Number(t.quality_rate || 0),
      input: Number(t.required_input || 0),
      output: Number(t.required_output || 0),
      loss: Math.max(0, Number(t.required_input || 0) - Number(t.required_output || 0)),
    }));


    const carbonSources = [
      { name: "Electricity", value: Number(result?.overall?.carbon?.electricity || 0) },
      { name: "Gas", value: Number(result?.overall?.carbon?.gas || 0) },
    ].filter(x => x.value > 0);

    const cellCapacityKwh = Number(result?.product?.cell_capacity_kwh || 0);
    const dailyProductionKwh = cellsDay * cellCapacityKwh;
    const costPerKwh = dailyProductionKwh ? totalCost / dailyProductionKwh : 0;
    const carbonPerKwh = dailyProductionKwh ? Number(result?.overall?.carbon?.total || 0) / dailyProductionKwh : 0;
    const operatingCostPerCell = cellsDay ? operating / cellsDay : 0;
    const materialCostPerCell = cellsDay ? materials / cellsDay : 0;

    const bottleneck = result?.bottleneck || null;

    const dryRoom = (Array.isArray(result?.environments) ? result.environments : [])
      .find(env => env?.environment_type === "dry_room") || null;

    const dryRoomCapacity = dryRoom ? {
      code: dryRoom.code || "DR-01",
      requiredArea: Number(dryRoom.controlled_area_m2 || 0),
      designArea: Number(dryRoom.design_area_m2 || 0),
      utilization: Number(dryRoom.capacity_utilization_pct || 0),
      exceeded: Boolean(dryRoom.capacity_exceeded),
      warning: dryRoom.capacity_warning || "",
    } : null;

    return {
      totalCost,
      totalEnergy,
      totalCarbon: Number(metric(result, ["overall", "carbon", "total"],
        metric(result, ["carbon", "total"], 0))),
      machines: Number(metric(result, ["overall", "machines"], 0)),
      operators: Number(metric(result, ["overall", "operators"], 0)),
      throughput: Number(metric(result, ["capacity", "required_good_cells_day"],
        metric(result, ["required_good_cells_day"], scenario?.throughput ?? 0))),
      costBreakdown: [
        { name: "Operating", value: operating },
        { name: "Materials", value: materials },
      ].filter(x => x.value > 0),
      energyBreakdown: [
        { name: "Electricity", value: electricity },
        { name: "Gas", value: gas },
      ].filter(x => x.value > 0),
      materialRequirements: materialRequirements
        .filter(x => !/(units|number of cells|cells$)/i.test(x.name))
        .sort((a, b) => b.value - a.value),
      topEnergy: top("totalEnergy"),
      topCost: top("totalCost"),
      topCarbon: top("totalCarbon"),
      branches: Object.values(branchMap),
      technologies: techRows,
      bottleneck,
      operatingBreakdown,
      materialCostByBranch,
      materialComponentKeys,
      branchEnergy: Object.values(branchEnergyMap),
      qualityFlow,
      carbonSources,
      annualEnergyKwh,
      dailyProductionKwh,
      costPerKwh,
      carbonPerKwh,
      operatingCostPerCell,
      materialCostPerCell,
      dryRoomCapacity,
    };
  }, [result, scenario]);

  const comparisonData = useMemo(() => scenarios.map(s => ({
    name: s.scenario_name || `Scenario ${s.scenario_id}`,
    cost: Number(s.total_cost ?? 0),
    energy: Number(s.total_energy ?? 0),
    carbon: Number(s.total_carbon ?? 0),
    throughput: Number(s.throughput ?? 0),
  })), [scenarios]);

  if (loading) return <div className="analytics-page"><h1>Analytics</h1><p>Loading…</p></div>;

  return (
    <div className="analytics-page" style={{ padding: 24 }}>
      <div style={{ display: "flex", justifyContent: "space-between", gap: 24, alignItems: "flex-start", flexWrap: "wrap", marginBottom: 8 }}>
        <div>
          <h1 style={{ margin: 0, lineHeight: 1.05 }}>Manufacturing Analytics</h1>
          <p style={{ margin: "10px 0 0", lineHeight: 1.4 }}>Explore cost, energy, carbon, capacity and material drivers from saved simulations.</p>
        </div>
        <label>
          <strong>Scenario</strong><br />
          <select value={selectedId} onChange={handleScenarioChange} style={{ minWidth: 260, padding: 8 }}>
            {scenarios.map(s => (
              <option key={s.scenario_id} value={s.scenario_id}>
                {s.scenario_name} · {s.line_type}
              </option>
            ))}
          </select>
        </label>
      </div>

      {error && <p style={{ padding: 12, border: "1px solid currentColor" }}>{error}</p>}
      {!scenario && !error && <p>No saved scenarios yet. Run and save a simulation to populate Analytics.</p>}

      {scenario && <>
        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(170px, 1fr))", gap: 12, margin: "22px 0" }}>
          {[
            ["Total Cost", fmt(analytics.totalCost, 2), "€/day"],
            ["Total Energy", fmt(analytics.totalEnergy, 2), "kWh/day"],
            ["Carbon", fmt(analytics.totalCarbon, 2), "kg CO₂-eq/day"],
            ["Machines", fmt(analytics.machines), "machines"],
            ["Operators", fmt(analytics.operators), "operators"],
            ["Cells / Day", fmt(analytics.throughput), "cells/day"],
          ].map(([label, value, unit]) => (
            <div key={label} style={{ padding: 16, border: "1px solid #ddd", borderRadius: 10 }}>
              <div style={{ fontSize: 13, opacity: .7 }}>{label}</div>
              <div style={{ display: "flex", alignItems: "baseline", gap: 6, flexWrap: "wrap" }}>
                <strong style={{ fontSize: 22 }}>{value}</strong>
                <span style={{ fontSize: 12, color: "#64748b" }}>{unit}</span>
              </div>
            </div>
          ))}
        </div>

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(190px, 1fr))", gap: 12, marginBottom: 18 }}>
		{[
		  ["Cost intensity (€/kWh)", analytics.costPerKwh, "€/kWh"],
		  ["Carbon intensity (kg CO₂-eq/kWh)", analytics.carbonPerKwh, "kg CO₂-eq/kWh"],
		  ["Operating cost (€/cell)", analytics.operatingCostPerCell, "€/cell"],
		  ["Material cost (€/cell)", analytics.materialCostPerCell, "€/cell"],
		].map(([label, value, unit]) => (
		  <div
			key={label}
			style={{
			  padding: 14,
			  borderRadius: 10,
			  background: "#f8fafc",
			  border: "1px solid #dbe3ef"
			}}
		  >
			<div style={{ fontSize: 14, opacity: 0.7 }}>
			  {label}
			</div>

			<div style={{ display: "flex", alignItems: "baseline", gap: 7 }}>
			  <strong style={{ fontSize: 19 }}>
				{Number(value).toLocaleString(undefined, {
				  minimumFractionDigits: 4,
				  maximumFractionDigits: 4
				})}
			  </strong>

			  <span style={{ fontSize: 12, opacity: 0.8 }}>
				{unit}
			  </span>
			</div>
		  </div>
		))}
        </div>

        <div style={{ fontSize: 12, color: "#64748b", margin: "-8px 0 18px" }}>
          Intensities normalize the simulated daily cost/carbon results by the production basis. Currency is shown as € where your model's cost inputs are in euros; carbon is shown as kg CO₂-eq.
        </div>

        {analytics.bottleneck && (
          <div style={{ padding: 16, borderRadius: 12, background: "#fff7ed", border: "1px solid #fdba74", marginBottom: 18 }}>
            <strong style={{ color: "#c2410c" }}>Bottleneck: {analytics.bottleneck.technology_name}</strong>
            <span style={{ marginLeft: 16 }}>
              {analytics.bottleneck.branch} · {analytics.bottleneck.process} · {fmt(analytics.bottleneck.machines?.machines)} machines · {fmt(analytics.bottleneck.energy?.total, 2)} kWh/day · €{fmt(analytics.bottleneck.costs?.total, 2)}/day
            </span>
          </div>
        )}

        {analytics.dryRoomCapacity?.exceeded && (
          <div style={{ padding: 16, borderRadius: 12, background: "#fff7ed", border: "1px solid #fb923c", marginBottom: 18 }}>
            <strong style={{ color: "#c2410c" }}>Dry Room capacity warning — calculation continues.</strong>
            <span style={{ marginLeft: 10 }}>
              {analytics.dryRoomCapacity.warning ||
                `${analytics.dryRoomCapacity.code} requires ${fmt(analytics.dryRoomCapacity.requiredArea, 2)} m² vs ${fmt(analytics.dryRoomCapacity.designArea, 2)} m² design area (${fmt(analytics.dryRoomCapacity.utilization, 2)}%).`}
            </span>
          </div>
        )}

        <div style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(340px, 1fr))", gap: 18 }}>
          <ChartCard title="Cost Breakdown (€/day)">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart><Pie data={analytics.costBreakdown} dataKey="value" nameKey="name" outerRadius={105} label>
                {analytics.costBreakdown.map((_, i) => <Cell key={i} fill={COST_COLORS[i % COST_COLORS.length]} />)}
              </Pie><Tooltip formatter={v => fmt(v, 2)} /><Legend /></PieChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Energy Mix (kWh/day)">
            <ResponsiveContainer width="100%" height={300}>
              <PieChart><Pie data={analytics.energyBreakdown} dataKey="value" nameKey="name" outerRadius={105} label>
                {analytics.energyBreakdown.map((_, i) => <Cell key={i} fill={ENERGY_COLORS[i % ENERGY_COLORS.length]} />)}
              </Pie><Tooltip formatter={v => fmt(v, 2)} /><Legend /></PieChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Largest Material Requirements">
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={analytics.materialRequirements.slice(0, 8)} layout="vertical" margin={{ left: 35 }}>
                <CartesianGrid strokeDasharray="3 3" /><XAxis type="number" tickFormatter={compact} />
                <YAxis type="category" dataKey="name" width={125} />
                <Tooltip formatter={v => `${fmt(v, 2)} kg`} /><Bar dataKey="value" name="kg" fill="#8b5cf6" />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Operating Cost Build-up (€/day)">
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={analytics.operatingBreakdown} margin={{ top: 8, right: 8, left: 8, bottom: 28 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" interval={0} angle={-18} textAnchor="end" height={55} tick={{ fontSize: 11 }} /><YAxis tickFormatter={compact} />
                <Tooltip formatter={v => [`€${fmt(v, 2)}`, "Cost"]} />
                <Bar dataKey="value" name="Cost">
                  {analytics.operatingBreakdown.map((_, i) => <Cell key={i} fill={COLORS[i % COLORS.length]} />)}
                </Bar>
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>


          <ChartCard title="Material Cost by Manufacturing Branch (€/day)">
            <ResponsiveContainer width="100%" height={360}>
              <BarChart data={analytics.materialCostByBranch}>
                <CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="name" /><YAxis tickFormatter={compact} />
                <Tooltip formatter={(v, name) => [`€${fmt(v, 2)}`, String(name).replaceAll("_", " ")]} />
                <Legend formatter={name => String(name).replaceAll("_", " ")} />
                {analytics.materialComponentKeys.map((key, i) => (
                  <Bar key={key} dataKey={key} stackId="materials" name={key} fill={COLORS[i % COLORS.length]} />
                ))}
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Energy by Manufacturing Branch (kWh/day)">
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={analytics.branchEnergy}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="branch" /><YAxis tickFormatter={compact} />
                <Tooltip formatter={v => fmt(v, 2)} /><Legend />
                <Bar dataKey="electricity" stackId="energy" fill="#06b6d4" name="Electricity" />
                <Bar dataKey="gas" stackId="energy" fill="#f97316" name="Gas" />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Carbon Source Breakdown (kg CO₂-eq/day)">
            <ResponsiveContainer width="100%" height={320}>
              <PieChart>
                <Pie data={analytics.carbonSources} dataKey="value" nameKey="name" outerRadius={105} label>
                  {analytics.carbonSources.map((_, i) => <Cell key={i} fill={ENERGY_COLORS[i % ENERGY_COLORS.length]} />)}
                </Pie>
                <Tooltip formatter={v => fmt(v, 2)} /><Legend />
              </PieChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Highest Energy Technologies (kWh/day)">
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={analytics.topEnergy} layout="vertical" margin={{ left: 35 }}>
                <CartesianGrid strokeDasharray="3 3" /><XAxis type="number" tickFormatter={compact} />
                <YAxis type="category" dataKey="name" width={125} />
                <Tooltip formatter={(v, name) => [`${fmt(v, 2)} kWh/day`, name]} /><Legend />
                <Bar dataKey="energy" stackId="energy" name="Equipment" fill="#06b6d4" />
                <Bar dataKey="dryRoomEnergy" stackId="energy" name="Dry Room" fill="#f97316" />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Highest Cost Technologies (€/day)">
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={analytics.topCost} layout="vertical" margin={{ left: 35 }}>
                <CartesianGrid strokeDasharray="3 3" /><XAxis type="number" tickFormatter={compact} />
                <YAxis type="category" dataKey="name" width={125} />
                <Tooltip formatter={(v, name) => [`€${fmt(v, 2)}/day`, name]} /><Legend />
                <Bar dataKey="cost" stackId="cost" name="Equipment" fill="#2563eb" />
                <Bar dataKey="dryRoomCost" stackId="cost" name="Dry Room" fill="#f59e0b" />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Highest Carbon Technologies (kg CO₂-eq/day)">
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={analytics.topCarbon} layout="vertical" margin={{ left: 35 }}>
                <CartesianGrid strokeDasharray="3 3" /><XAxis type="number" tickFormatter={compact} />
                <YAxis type="category" dataKey="name" width={125} />
                <Tooltip formatter={(v, name) => [`${fmt(v, 2)} kg CO₂-eq/day`, name]} /><Legend />
                <Bar dataKey="carbon" stackId="carbon" name="Equipment" fill="#10b981" />
                <Bar dataKey="dryRoomCarbon" stackId="carbon" name="Dry Room" fill="#8b5cf6" />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Resources by Manufacturing Branch">
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={analytics.branches}>
                <CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="branch" />
                <YAxis /><Tooltip /><Legend />
                <Bar dataKey="machines" name="Machines" fill="#2563eb" />
                <Bar dataKey="operators" name="Operators" fill="#f59e0b" />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>

          <ChartCard title="Scenario Cost Comparison (€/day)">
            <ResponsiveContainer width="100%" height={320}>
              <BarChart data={comparisonData} margin={{ bottom: 50 }}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis dataKey="name" angle={-25} textAnchor="end" height={70} />
                <YAxis tickFormatter={compact} /><Tooltip formatter={v => fmt(v, 2)} />
                <Bar dataKey="cost" name="Total Cost" fill="#8b5cf6" />
              </BarChart>
            </ResponsiveContainer>
          </ChartCard>
        </div>

        <ChartCard title="Technology Detail" wide>
          <div style={{ overflowX: "auto" }}>
            <table style={{ width: "100%", borderCollapse: "collapse" }}>
              <thead><tr>{["Technology","Process","Branch","Environment","Machines","Operators","Equipment Energy","Dry Room Energy","Total Energy","DR Energy Share","Equipment Cost","Dry Room Cost","Total Cost","DR Cost Share","Equipment Carbon","Dry Room Carbon","Total Carbon","DR Carbon Share"].map(h =>
                <th key={h} style={{ textAlign: "left", padding: 8, borderBottom: "1px solid #ddd" }}>{h}</th>)}</tr></thead>
              <tbody>{analytics.technologies.map((r, i) => <tr key={`${r.name}-${i}`}>
                <td style={{ padding: 8 }}>{r.name}</td><td>{r.process}</td><td>{r.branch}</td>
                <td>{String(r.environment || "none").replaceAll("_", " ")}</td>
                <td>{fmt(r.machines)}</td><td>{fmt(r.operators)}</td>
                <td>{fmt(r.energy, 2)}</td><td>{fmt(r.dryRoomEnergy, 2)}</td><td>{fmt(r.totalEnergy, 2)}</td><td>{fmt(r.dryRoomEnergyShare, 1)}%</td>
                <td>{fmt(r.cost, 2)}</td><td>{fmt(r.dryRoomCost, 2)}</td><td>{fmt(r.totalCost, 2)}</td><td>{fmt(r.dryRoomCostShare, 1)}%</td>
                <td>{fmt(r.carbon, 2)}</td><td>{fmt(r.dryRoomCarbon, 2)}</td><td>{fmt(r.totalCarbon, 2)}</td><td>{fmt(r.dryRoomCarbonShare, 1)}%</td>
              </tr>)}</tbody>
            </table>
          </div>
        </ChartCard>
      </>}
    </div>
  );
}

function ChartCard({ title, children }) {
  return (
    <section style={{ padding: 16, border: "1px solid #dbe3ef", borderRadius: 12, minWidth: 0, marginTop: 18, background: "#fff", boxShadow: "0 2px 10px rgba(15,23,42,.04)" }}>
      <h3 style={{ marginTop: 0 }}>{title}</h3>
      {children}
    </section>
  );
}
