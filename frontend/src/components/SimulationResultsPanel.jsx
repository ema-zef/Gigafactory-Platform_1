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
            : simulationResults?.simulation ??
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
        technology: row.technology_name,
        process: row.process,
        unit: row.unit,
        output: Number(row.required_output),
        input: Number(row.required_input),
        yield: Number(row.quality_rate)
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

                <h3>
                    Cells per Day by Process
                </h3>

                <ResponsiveContainer width="100%" height={360}>

                    <BarChart data={rows}>

                        <CartesianGrid strokeDasharray="3 3" />

                        <XAxis
                            dataKey="technology"
                            angle={-35}
                            textAnchor="end"
                            interval={0}
                            height={90}
                        />

                        <YAxis />

                        <Tooltip />

                        <Bar
                            dataKey="output"
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

                                <th>Process</th>

                                <th>Unit</th>

                                <th>Output</th>

                                <th>Input</th>

                                <th>Yield</th>

                            </tr>

                        </thead>

                        <tbody>

                            {rows.map((row, index) => (

                                <tr key={index}>

                                    <td>{row.technology}</td>

                                    <td>{row.process}</td>

                                    <td>{row.unit}</td>

                                    <td>{Math.round(row.output).toLocaleString()}</td>

                                    <td>{Math.round(row.input).toLocaleString()}</td>

                                    <td>{row.yield.toFixed(2)}%</td>

                                </tr>

                            ))}

                        </tbody>

                    </table>

                </div>

            </div>

        </div>

    );

}