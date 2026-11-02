import "./SimulationResultsPanel.css";

import {
    ResponsiveContainer,
    BarChart,
    CartesianGrid,
    XAxis,
    YAxis,
    Tooltip,
    Bar
} from "recharts";

export default function SimulationResultsPanel({ simulationResults }) {

    // Accept either an array or an object containing simulation
    const simulation =
        Array.isArray(simulationResults)
            ? simulationResults
            : simulationResults?.technologies ??
              simulationResults?.simulation ??
              simulationResults?.results ??
              [];

    // No simulation yet
    if (simulation.length === 0) {
        return (
            <div className="simulation-panel">

                <div className="simulation-empty">

                    <h2>Simulation Results</h2>

                    <p>
                        Configure the manufacturing route and click
                        <strong> Run Simulation</strong>.
                    </p>

                </div>

            </div>
        );
    }

    // Build chart/table rows from backend response
    const rows = simulation.map(row => ({
        technology: `${row.branch ? `${row.branch} · ` : ""}${row.technology_name}`,
        unit: row.unit,
        output: Number(row.required_output),
        cost: Number(row.costs?.total ?? 0),
        branch: row.branch ?? "",
        process: row.process ?? "",
        batches: row.batches ?? "-",
        machines: row.machines?.machines ?? 0,
        shifts: row.machines?.uptime ?? "-",
        operators: row.operators?.operators_min ?? 0,
    }));

    const finalRow = simulation.at(-1);
	
    const avgQuality = (
        simulation.reduce(
            (sum, row) => sum + Number(row.quality_rate),
            0
        ) / simulation.length
    ).toFixed(2);

    return (

        <div className="simulation-panel">

            <h2 className="simulation-title">
                Simulation Results
            </h2>

            {/* KPI CARDS */}

            <div className="kpi-grid">

                <div className="kpi-card">

                    <div className="kpi-label">
                        Daily Production
                    </div>

                    <div className="kpi-value">
                        {Math.round(finalRow.required_output).toLocaleString()}
                    </div>

                    <div className="kpi-unit">
                        cells/day
                    </div>

                </div>

                <div className="kpi-card">

                    <div className="kpi-label">
                        Number of Processes
                    </div>

                    <div className="kpi-value">
                        {simulation.length}
                    </div>

                </div>

                <div className="kpi-card">

                    <div className="kpi-label">
                        Average Quality
                    </div>

                    <div className="kpi-value">
                        {avgQuality}%
                    </div>

                </div>

                <div className="kpi-card success">

                    <div className="kpi-label">
                        Bottleneck Yield
                    </div>

                    <div className="kpi-value">
                        {Number(finalRow.quality_rate).toFixed(2)}%
                    </div>

                </div>

            </div>

            {/* BAR CHART */}

			<div className="chart-card">
				<h3>Cost by Process (€)</h3>

				<ResponsiveContainer width="100%" height={360}>
					<BarChart
						data={rows}
						margin={{ top: 10, right: 20, left: 20, bottom: 20 }}
					>
						<CartesianGrid strokeDasharray="3 3" />

						<XAxis
							dataKey="technology"
							angle={-35}
							textAnchor="end"
							interval={0}
							height={90}
						/>

						<YAxis
							tickFormatter={value => Number(value).toLocaleString()}
						/>

						<Tooltip
							formatter={value => [
								Number(value).toLocaleString(undefined, {
									minimumFractionDigits: 2,
									maximumFractionDigits: 2,
								}),
								"Cost",
							]}
						/>

						<Bar
							dataKey="cost"
							name="Cost"
							fill="#1f4b8f"
						/>
					</BarChart>
				</ResponsiveContainer>
			</div>

            {/* TABLE */}

            <div className="table-card">

                <h3>
                    Process Stream Summary
                </h3>

                <div className="results-table-wrapper">

                    <table className="results-table">

                        <thead>

                            <tr>
                                <th>Technology</th>
                                <th>Unit</th>
                                <th>Output</th>
                                <th>Batches</th>
                                <th>Machines</th>
                                <th>Shifts</th>
                                <th>Operators/day</th>
                            </tr>

                        </thead>

                        <tbody>

                            {rows.map((row, index) => (

                                <tr key={index}>
                                    <td>{row.technology}</td>
                                    <td>{row.unit}</td>
                                    <td>{Math.round(row.output).toLocaleString()}</td>
                                    <td>{row.batches}</td>
                                    <td>{row.machines}</td>
                                    <td>{row.shifts}</td>
                                    <td>{row.operators}</td>
                                </tr>

                            ))}

                        </tbody>

                    </table>

                </div>

            </div>

        </div>

    );

}