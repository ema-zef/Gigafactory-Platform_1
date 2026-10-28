import { useEffect, useState } from "react";
import axios from "axios";
import { ResponsiveContainer, BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend } from "recharts";

import "./ManufacturingRouteBuilder.css";
import SimulationResultsPanel from "./SimulationResultsPanel";

export default function ManufacturingRouteBuilder({ user }) {
    // Per-account, per-browser route drafts; never restore another account's draft.
    const storage = {
      getItem: key => sessionStorage.getItem(`sota:${user.id}:${key}`),
      setItem: (key, value) => sessionStorage.setItem(`sota:${user.id}:${key}`, value),
      removeItem: key => sessionStorage.removeItem(`sota:${user.id}:${key}`),
    };

    /* =====================================================
       API
    ===================================================== */

    const API =
        import.meta.env.VITE_API_URL ||
        "http://localhost:8000";

/* ===========================================
   Plant & Product
=========================================== */

const [plantOptions, setPlantOptions] = useState([]);
const [productOptions, setProductOptions] = useState([]);
const [selectedPlant, setSelectedPlant] = useState("");
const [selectedProduct, setSelectedProduct] = useState("");

/* Prevent saving before the initial restore is complete */
const [isLoaded, setIsLoaded] = useState(false);

    /* =====================================================
       Equipment
    ===================================================== */

    const [equipmentOptions, setEquipmentOptions] = useState([]);

useEffect(() => {

    Promise.all([
        loadEquipment(),
        loadPlants(),
        loadProducts()
    ]);

}, []);

    async function loadEquipment() {

    try {

        const res = await axios.get(`${API}/equipment`);

        console.log("Equipment loaded:", res.data);

        setEquipmentOptions(res.data ?? []);

    }

    catch (err) {

        console.error("Equipment load failed:", err);

        setEquipmentOptions([]);

    }

}

async function loadPlants() {

    try {

        const res = await axios.get(
            `${API}/production_configuration/selectable`
        );

        console.log("Plants loaded:", res.data);

        setPlantOptions(
            Array.isArray(res.data)
                ? res.data
                : []
        );

    }

    catch (err) {

        console.error("Plant load failed:", err);

        setPlantOptions([]);

    }

}

async function loadProducts() {

    try {

        const res = await axios.get(
            `${API}/product_configuration/selectable`
        );

        console.log("Products loaded:", res.data);

        setProductOptions(
            Array.isArray(res.data)
                ? res.data
                : []
        );

    }

    catch (err) {

        console.error("Product load failed:", err);

        setProductOptions([]);

    }

}

    /* =====================================================
       Simulation
    ===================================================== */


    const [simulationResults, setSimulationResults] = useState([]);
    const [lastRunKey, setLastRunKey] = useState(null);
    const [savedScenarios, setSavedScenarios] = useState([]);
    const [scenarioName, setScenarioName] = useState("");
    const [lineType, setLineType] = useState("Gigafactory");
    const [scenarioBusy, setScenarioBusy] = useState(false);
    const [compareA, setCompareA] = useState("");
    const [compareB, setCompareB] = useState("");
    const [comparison, setComparison] = useState(null);


    async function refreshScenarios() {
        try {
            const response = await axios.get(`${API}/scenarios`);
            setSavedScenarios(response.data ?? []);
        } catch (error) {
            console.error("Loading scenarios failed", error);
        }
    }

    useEffect(() => { refreshScenarios(); }, []);

    async function loadScenario(id) {
        if (!id) return;
        try {
            const { data } = await axios.get(`${API}/scenarios/${id}`);
            const config = data.route_json;
            if (!config || !data.result_json) throw new Error("Incomplete scenario snapshot");
            setSelectedPlant(String(config.plant_id));
            setSelectedProduct(String(config.product_id));
            const restore = steps => steps?.length ? steps.map(step => ({
                ...step, id: crypto.randomUUID(),
                equipment_id: step.equipment_id ?? step.technology_id,
                environment: step.environment ?? "none",
                execution_mode: step.execution_mode ?? "in_house",
            })) : [createStep()];
            setCathodeSteps(restore(config.cathode_route));
            setAnodeSteps(restore(config.anode_route));
            setAssemblySteps(restore(config.assembly_route));
            setSimulationResults(data.result_json);
            // Loaded snapshots are viewable; rerun before saving them as a new scenario.
            setLastRunKey(null);
            setComparison(null);
        } catch (error) {
            alert(error.response?.data?.detail || error.message || "Unable to load scenario");
        }
    }

    async function deleteScenario(id) {
        if (!window.confirm("Delete this saved scenario and its results?")) return;
        try {
            await axios.delete(`${API}/scenarios/${id}`);
            setComparison(null);
            await refreshScenarios();
        } catch (error) {
            alert(error.response?.data?.detail || "Unable to delete scenario");
        }
    }

    async function toggleSoa(scenario) {
        try {
            if (scenario.is_soa) {
                await axios.delete(`${API}/scenarios/${scenario.scenario_id}/soa`);
            } else {
                await axios.put(`${API}/scenarios/${scenario.scenario_id}/soa`, {
                    line_type: scenario.line_type,
                });
            }
            await refreshScenarios();
        } catch (error) {
            alert(error.response?.data?.detail || "Unable to update SoA");
        }
    }

    async function compareScenarios() {
        if (!compareA || !compareB || compareA === compareB) {
            alert("Select two different saved scenarios.");
            return;
        }
        try {
            const [a, b] = await Promise.all([
                axios.get(`${API}/scenarios/${compareA}`),
                axios.get(`${API}/scenarios/${compareB}`),
            ]);
            setComparison([a.data, b.data]);
        } catch (error) {
            alert(error.response?.data?.detail || "Unable to compare scenarios");
        }
    }

     const totalComparisonMetrics = comparison ? [
         { title: "Total Cost", key: "total_cost", nested: "costs", unit: "cost units" },
         { title: "Total Energy", key: "total_energy", nested: "energy", unit: "energy units" },
         { title: "Total Carbon", key: "total_carbon", nested: "carbon", unit: "carbon units" },
     ].map(metric => ({
         ...metric,
         data: comparison.map(scenario => ({
             name: scenario.scenario_name,
             value: Number(scenario[metric.key] ?? scenario.result_json?.overall?.[metric.nested]?.total ?? 0),
         })),
     })) : [];

    /* =====================================================
       Route Template
    ===================================================== */

    const createStep = () => ({

        id: crypto.randomUUID(),
		equipment_id: null,

        technology_id: null,

        technology_name: "",

        process: "",

        process_category: "",
        execution_mode: "in_house",

        quality_rate: "",

        environment: "none"

    });

    /* =====================================================
       Manufacturing Routes
    ===================================================== */

    const [cathodeSteps, setCathodeSteps] = useState([

        createStep(),
        createStep(),
        createStep(),
        createStep(),
        createStep()

    ]);

    const [anodeSteps, setAnodeSteps] = useState([

        createStep(),
        createStep(),
        createStep(),
        createStep(),
        createStep()

    ]);

    const [assemblySteps, setAssemblySteps] = useState([

        createStep(),
        createStep(),
        createStep(),
        createStep()

    ]);
	

    const purchaseElectrode = (side) => {
        const setSteps = side === "cathode" ? setCathodeSteps : setAnodeSteps;
        setSteps([{
            ...createStep(),
            execution_mode: "purchased_intermediate",
            process: `Purchased finished ${side} electrode`,
            technology_name: `Purchased finished ${side} electrode`,
            process_category: "ROLL",
            input_material: `finished_${side}_electrode`,
            quality_rate: 100,
            fee_eur_per_unit: "",
            transport_eur_per_unit: 0,
            emissions_kgco2e_per_unit: 0,
        }]);
        setLastRunKey(null);
    };

    const routePayload = () => ({
        plant_id: Number(selectedPlant),
        product_id: Number(selectedProduct),
        plant_code: plantOptions.find(p => p.id === Number(selectedPlant))?.code || '',
        product_code: productOptions.find(p => p.id === Number(selectedProduct))?.code || '', 
        cathode_route: cathodeSteps.map(step => ({...step, process_category: String(step.process_category ?? "").trim().toUpperCase()})).filter(step => (step.execution_mode && step.execution_mode !== "in_house") || step.equipment_id != null),
        anode_route: anodeSteps.map(step => ({...step, process_category: String(step.process_category ?? "").trim().toUpperCase()})).filter(step => (step.execution_mode && step.execution_mode !== "in_house") || step.equipment_id != null),
        assembly_route: assemblySteps.map(step => ({...step, process_category: String(step.process_category ?? "").trim().toUpperCase()})).filter(step => (step.execution_mode && step.execution_mode !== "in_house") || step.equipment_id != null),
    });
	
    const currentRouteKey = JSON.stringify(routePayload());
	
    const canSaveScenario = Boolean(lastRunKey && lastRunKey === currentRouteKey &&
        simulationResults?.technologies?.length);	
	
	useEffect(() => {

    const savedPlant = storage.getItem("selectedPlant");
    const savedProduct = storage.getItem("selectedProduct");
    if (savedPlant) setSelectedPlant(savedPlant);

    if (savedProduct) setSelectedProduct(savedProduct);

    const savedCathode = storage.getItem("cathodeRoute");
    const savedAnode = storage.getItem("anodeRoute");
    const savedAssembly = storage.getItem("assemblyRoute");

    if (savedCathode)
        setCathodeSteps(JSON.parse(savedCathode));

    if (savedAnode)
        setAnodeSteps(JSON.parse(savedAnode));

    if (savedAssembly)
        setAssemblySteps(JSON.parse(savedAssembly));
  
	const savedSimulation = 
	    storage.getItem("simulationResults");

    if (savedSimulation) 
        setSimulationResults(
            JSON.parse(savedSimulation)
	    );

    setIsLoaded(true);
   
}, []);

useEffect(() => {

    if (!isLoaded) return;
	
	storage.setItem(
        "selectedPlant",
        selectedPlant
    );

}, [selectedPlant, isLoaded]);

useEffect(() => {
 
    if (!isLoaded) return;
 
    storage.setItem(
        "selectedProduct",
        selectedProduct
    );

}, [selectedProduct, isLoaded]);


useEffect(() => {

    if (!isLoaded) return;
	
	storage.setItem(

        "cathodeRoute",

        JSON.stringify(cathodeSteps)

    );

}, [cathodeSteps, isLoaded]);

useEffect(() => {

   if (!isLoaded) return;

   storage.setItem(

        "anodeRoute",

        JSON.stringify(anodeSteps)

    );

}, [anodeSteps, isLoaded]);

useEffect(() => {

    if (!isLoaded) return;
	
	storage.setItem(

        "assemblyRoute",

        JSON.stringify(assemblySteps)

    );

}, [assemblySteps, isLoaded]);

useEffect(() => {

    if (!isLoaded) return;

    storage.setItem(

        "simulationResults",

        JSON.stringify(simulationResults)

    );

}, [simulationResults, isLoaded]);

    /* =====================================================
       Helpers
    ===================================================== */


    function addStep(steps, setSteps) {

        setSteps([

            ...steps,

            createStep()

        ]);

    }

    function deleteStep(index, steps, setSteps) {

    // Always keep at least one empty row
    if (steps.length === 1) {

        setSteps([createStep()]);

        return;

    }

    const copy = [...steps];

    copy.splice(index, 1);

    setSteps(copy);

}

    function moveStepUp(index, steps, setSteps) {

        if (index === 0) return;

        const copy = [...steps];

        [copy[index - 1], copy[index]] =
            [copy[index], copy[index - 1]];

        setSteps(copy);

    }

    function moveStepDown(index, steps, setSteps) {

        if (index >= steps.length - 1) return;

        const copy = [...steps];

        [copy[index], copy[index + 1]] =
            [copy[index + 1], copy[index]];

        setSteps(copy);

    }

    function updateField(index, field, value, steps, setSteps) {
        setSteps(steps.map((step, i) => i === index ? { ...step, [field]: value,
            ...(field === "execution_mode" && value !== "in_house" ? { equipment_id: null, technology_id: null, environment: "none" } : {})
        } : step));
    }

    function updateEquipment(index, equipmentId, steps, setSteps) {

    const equipment = equipmentOptions.find(

        eq => Number(eq.id) === Number(equipmentId)

    );

    if (!equipment) {
        updateField(index, "equipment_id", null, steps, setSteps);
        return;
    }

    const copy = [...steps];

    copy[index] = {

        ...copy[index],

        equipment_id: equipment.id,

        technology_id: equipment.id,

        technology_name: equipment.technology_name,

        process: equipment.process,

        process_category: String(equipment.process_category ?? "").trim().toUpperCase(),

        quality_rate: equipment.quality_rate,
        execution_mode: "in_house"

    };

    setSteps(copy);

}

    function updateEnvironment(index, environment, steps, setSteps) {
        const copy = [...steps];

        copy[index] = {
            ...copy[index],
            environment
        };

        setSteps(copy);
    }

    /* =====================================================
   Save Manufacturing Route
===================================================== */

async function saveScenario() {
    if (!canSaveScenario) {
        alert("Run Simulation for the current route before saving a scenario.");
        return;
    }
    if (!scenarioName.trim()) {
        alert("Enter a scenario name before saving.");
        return;
    }
    setScenarioBusy(true);
    try {
        const response = await axios.post(`${API}/scenarios`, {
            scenario_name: scenarioName.trim(),
            line_type: lineType,
            configuration: routePayload(),
        });
        setSimulationResults(response.data.result);
        setScenarioName("");
        await refreshScenarios();
        alert("Scenario saved successfully.");
    } catch (error) {
        alert(error.response?.data?.detail || "Unable to save scenario.");
    } finally {
        setScenarioBusy(false);
    }
}

function resetRoute() {

    setCathodeSteps([
        createStep(),
        createStep(),
        createStep(),
        createStep(),
        createStep()
    ]);

    setAnodeSteps([
        createStep(),
        createStep(),
        createStep(),
        createStep(),
        createStep()
    ]);

    setAssemblySteps([
        createStep(),
        createStep(),
        createStep(),
        createStep()
    ]);

    setSimulationResults([]);
    setLastRunKey(null);
    setComparison(null);
	
	storage.removeItem("selectedPlant");
    storage.removeItem("selectedProduct");
    storage.removeItem("cathodeRoute");
    storage.removeItem("anodeRoute");
    storage.removeItem("assemblyRoute");
	storage.removeItem("simulationResults");

}

async function handleRunSimulation() {
    const runKey = currentRouteKey;
    setLastRunKey(null);

    if (!selectedPlant || !selectedProduct) {

        alert(
            "Please select Plant and Product before running the simulation."
        );

        return;

    }

    const payload = routePayload();
    for (const side of ["cathode", "anode"]) {
        const route = payload[`${side}_route`];
        if (route.length === 0) {
            alert(`${side}: no route selected. Add in-house steps or choose Buy finished electrode.`);
            return;
        }
        const purchases = route.filter(step => step.execution_mode === "purchased_intermediate");
        if (purchases.length && (purchases.length > 1 || route[0] !== purchases[0])) {
            alert(`${side}: a purchased intermediate must be the first step and appear only once.`);
            return;
        }
        for (const purchase of purchases) {
            if (!purchase.input_material?.trim() || purchase.fee_eur_per_unit === "" ||
                purchase.fee_eur_per_unit == null || !Number.isFinite(Number(purchase.fee_eur_per_unit)) ||
                Number(purchase.fee_eur_per_unit) < 0) {
                alert(`${side}: enter an intermediate material name and a valid purchase price.`);
                return;
            }
        }
    }

    console.log(JSON.stringify(payload, null, 2));

    try {

        const response = await axios.post(

            `${API}/simulation/run`,

            payload

        );

        console.log("Simulation Results:", response.data);
		console.log(response.data.result);
        console.log(JSON.stringify(response.data.result, null, 2));
        const result = response.data.result;
        console.log("OVERALL:", JSON.stringify(result.overall, null, 2));

        console.log(
            "OUTSOURCED COATING:",
            JSON.stringify(
                result.technologies?.find(
                    t =>
                        t.branch === "cathode" &&
                        t.execution_mode === "outsourced" &&
                        t.process === "Coating & Drying"
                ) ?? null,
                null,
                2
            )
        );

        setSimulationResults(response.data.result);
        setLastRunKey(runKey);

        storage.setItem(
             "simulationResults",
             JSON.stringify(response.data.result)
        );
    }

    catch (err) {

        console.error("Simulation failed:", err);

        setSimulationResults([]);

        alert(

            err.response?.data?.detail ||

            "Simulation failed."

        );

    }

}

/* =====================================================
   Route Table Renderer
===================================================== */

function renderRouteTable({

    title,

    steps,

    setSteps

}) {

    return (

        <div className="route-card">

            <h2 className="route-title">

                {title}

            </h2>

            <div className="table-wrapper">

                <table className="route-table">

    <colgroup>

        <col style={{ width: "45px" }} />
        <col style={{ width: "180px" }} />
        <col style={{ width: "130px" }} />
        <col style={{ width: "110px" }} />
        <col style={{ width: "145px" }} />
        <col style={{ width: "70px" }} />
        <col style={{ width: "75px" }} />

    </colgroup>

                    <thead>

                        <tr>

                            <th className="step-col">

                                #

                            </th>

                            <th className="equipment-col">

                                Equipment

                            </th>

                            <th className="process-col">

                                Process

                            </th>

                            <th className="category-col">

                                Category

                            </th>

                            <th className="environment-col">

                                Environment

                            </th>

                            <th className="quality-col">

                                Quality %

                            </th>

                            <th className="actions-col">

                                Actions

                            </th>

                        </tr>

                    </thead>

                    <tbody>

                        {steps.map((step, index) => (

                            <tr key={step.id}>

                                <td>

                                    {index + 1}

                                </td>

                                <td>

                                    <select value={step.execution_mode ?? "in_house"}
                                        aria-label="Execution mode"
                                        onChange={e => updateField(index, "execution_mode", e.target.value, steps, setSteps)}>
                                        <option value="in_house">In-house</option>
                                        <option value="outsourced">Outsourced processing</option>
                                        <option value="purchased_intermediate">Purchased intermediate</option>
                                    </select>
                                    {(step.execution_mode ?? "in_house") === "in_house" ? (
                                    <select

                                        value={step.equipment_id ?? ""}

                                        onChange={(e) =>

                                            updateEquipment(

                                                index,

                                                e.target.value,

                                                steps,

                                                setSteps

                                            )

                                        }

                                    >

                                        <option value="">

                                            Select Equipment

                                        </option>

                                        {equipmentOptions
										
										    .filter(eq => eq.technology_name)
											
											.slice()
										
										    .sort((a,b)=>
											
										        a.technology_name.localeCompare(
												
												    b.technology_name
										
										        )
												
										    )
										
										.map(eq => (

                                            <option

                                                key={eq.id}

                                                value={eq.id}

                                            >

                                                {eq.technology_name} 

                                            </option>

                                        ))}

                                    </select>
                                    ) : (
                                      <div style={{display:"grid",gap:4,minWidth:200,marginTop:6}}>
                                        <input placeholder="Process / intermediate name" value={step.process ?? ""}
                                            onChange={e => updateField(index,"process",e.target.value,steps,setSteps)} />
                                        <select value={step.process_category ?? ""}
                                            onChange={e => updateField(index,"process_category",e.target.value,steps,setSteps)}>
                                            <option value="">Select unit category</option>
                                            <option value="MASS">MASS · kg</option>
                                            <option value="ROLL">ROLL · metres</option>
                                            <option value="CELL">CELL · cells</option>
                                        </select>
                                        {step.execution_mode === "purchased_intermediate" &&
                                          <input placeholder="Intermediate material name" value={step.input_material ?? ""}
                                            onChange={e => updateField(index,"input_material",e.target.value,steps,setSteps)} />}
                                        <label>Fee / purchase price (€ per {step.process_category === "MASS" ? "kg" : step.process_category === "ROLL" ? "parent-web m" : "cell"})</label>
                                        <input type="number" min="0" step="any" value={step.fee_eur_per_unit ?? ""}
                                            onChange={e => updateField(index,"fee_eur_per_unit",e.target.value === "" ? "" : Number(e.target.value),steps,setSteps)} />
                                        <label>Transport (€ / unit)</label>
                                        <input type="number" min="0" step="any" value={step.transport_eur_per_unit ?? 0}
                                            onChange={e => updateField(index,"transport_eur_per_unit",Number(e.target.value),steps,setSteps)} />
                                        <label>Supplier emissions (kg CO₂e / unit)</label>
                                        <input type="number" min="0" step="any" value={step.emissions_kgco2e_per_unit ?? 0}
                                            onChange={e => updateField(index,"emissions_kgco2e_per_unit",Number(e.target.value),steps,setSteps)} />
                                        <label>Yield (%)</label>
                                        <input type="number" min="0.01" max="100" step="any" value={step.quality_rate || 100}
                                            onChange={e => updateField(index,"quality_rate",Number(e.target.value),steps,setSteps)} />
                                      </div>
                                    )}
									

                                </td>

                                <td>

                                    <input

                                        readOnly
										
										placeholder="Auto"

                                        value={step.process ?? ""}

                                    />

                                </td>

                                <td>

                                    <input

                                        readOnly
										
										placeholder="Auto"

                                        value={step.process_category ?? ""}

                                    />

                                </td>

                                <td className="environment-cell">
                                    <select
                                        aria-label={`Environment for ${step.technology_name || `step ${index + 1}`}`}
                                        value={step.environment ?? "none"}
                                        onChange={(e) =>
                                            updateEnvironment(
                                                index,
                                                e.target.value,
                                                steps,
                                                setSteps
                                            )
                                        }
                                    >
                                        <option value="none">None</option>
                                        <option value="dry_room">Dry Room — DR-01</option>
                                    </select>
                                </td>

                                <td className="quality-cell">

                                    <input

                                        readOnly
										
										placeholder="Auto"

                                        value={

                                            step.quality_rate != null

                                                ? `${Number(step.quality_rate).toFixed(2)}%`

                                                : ""

                                        }

                                    />

                                </td>

                                <td>

                                    <div className="route-actions-cell">

                                        <button
                                            
											disabled={index === 0}
											
                                            type="button"

                                            title="Move Up"

                                            onClick={() =>

                                                moveStepUp(

                                                    index,

                                                    steps,

                                                    setSteps

                                                )

                                            }

                                        >

                                            ▲

                                        </button>

                                        <button

                                            type="button"

                                            title="Move Down"

                                            onClick={() =>

                                                moveStepDown(

                                                    index,

                                                    steps,

                                                    setSteps

                                                )

                                            }

                                        >

                                            ▼

                                        </button>

                                        <button

                                            disabled={steps.length === 1}
   
                                            type="button"

                                            title="Delete"

                                            onClick={() =>

                                                deleteStep(

                                                    index,

                                                    steps,

                                                    setSteps

                                                )

                                            }

                                        >

                                            ✕

                                        </button>

                                    </div>

                                </td>

                            </tr>

                        ))}

                    </tbody>

                </table>

            </div>

            <button

                className="add-step-btn"

                onClick={() =>

                    addStep(

                        steps,

                        setSteps

                    )

                }

            >

                + Add Step

            </button>

        </div>

    );

}



return (

<div className="route-builder">

    {/* Floating buttons */}
    <div className="builder-header-actions">

        <button
            className="reset-route-btn"
            onClick={resetRoute}
        >
            Reset
        </button>

        <button
            className="save-route-btn"
            onClick={saveScenario}
            disabled={!canSaveScenario || scenarioBusy}
        >
            💾 Save Scenario
        </button>

        <button
            className="run-simulation-btn"
            onClick={handleRunSimulation}
        >
            ▶ Run Simulation
        </button>

    </div>



    {/* Page title */}
	<div className="builder-page-title">
		<div className="builder-title-text">
			<h1>Route Builder</h1>
			<p className="builder-subtitle">
				Design, simulate and optimize your battery cell production.
			</p>
		</div>

		<div className="scenario-save-controls">
			<input
				aria-label="Scenario name"
				placeholder="Scenario name"
				maxLength={100}
				value={scenarioName}
				onChange={event => setScenarioName(event.target.value)}
			/>

			<select
				aria-label="Line type"
				value={lineType}
				onChange={event => setLineType(event.target.value)}
			>
				<option value="Gigafactory">Gigafactory</option>
				<option value="Pilot Line">Pilot Line</option>
			</select>

			{!canSaveScenario && (
				<span>Run the current route to enable Save Scenario.</span>
			)}
		</div>
	</div>


    {/* ==========================================
        MAIN PAGE LAYOUT
    ========================================== */}

<div className="route-layout">

    {/* LEFT COLUMN */}
    <div className="route-left">

        <div className="selection-panel">

            {/* ---------- Plant ---------- */}

            <div className="route-card selection-card">

                <h2 className="route-title">Plant</h2>

                <select
                    value={selectedPlant}
                    onChange={(e) => setSelectedPlant(e.target.value)}
                >
                    <option value="">Select Plant</option>

                    {plantOptions.map((plant) => (
                        <option key={plant.id} value={plant.id}>
                            {plant.code}{plant.is_sota ? ` · SOTA ${plant.sota_line_type}` : ''}
                        </option>
                    ))}

                </select>

            </div>

            {/* ---------- Product ---------- */}

            <div className="route-card selection-card">

                <h2 className="route-title">Product</h2>

                <select
                    value={selectedProduct}
                    onChange={(e) => setSelectedProduct(e.target.value)}
                >
                    <option value="">Select Product</option>

                    {productOptions.map((product) => (
                        <option key={product.id} value={product.id}>
                            {product.code}{product.is_sota ? ` · SOTA ${product.sota_line_type}` : ''}
                        </option>
                    ))}

                </select>

            </div>

        </div>
        <button type="button" className="add-step-btn" onClick={() => purchaseElectrode("cathode")}>Buy finished cathode electrode</button>
        {renderRouteTable({
            title: "Cathode Route",
            steps: cathodeSteps,
            setSteps: setCathodeSteps
        })}

        <button type="button" className="add-step-btn" onClick={() => purchaseElectrode("anode")}>Buy finished anode electrode</button>
        {renderRouteTable({
            title: "Anode Route",
            steps: anodeSteps,
            setSteps: setAnodeSteps
        })}

        {renderRouteTable({
            title: "Assembly Route",
            steps: assemblySteps,
            setSteps: setAssemblySteps
        })}

    </div>

    {/* RIGHT COLUMN */}

    <div className="route-right">

        <SimulationResultsPanel
            simulationResults={simulationResults}
        />
        <section className="chart-card" style={{ marginTop: 16 }}>
            <h3>Saved Scenarios</h3>
            {savedScenarios.length === 0 && <p>No saved scenarios yet.</p>}
            {savedScenarios.map(scenario => (
                <div key={scenario.scenario_id} style={{ padding: "10px 0", borderBottom: "1px solid #ddd" }}>
                    <strong>{scenario.scenario_name}</strong> · {scenario.line_type}
                    {scenario.is_soa && <strong> · SOTA</strong>}
                    <div style={{ display: "flex", flexWrap: "wrap", gap: 6, marginTop: 6 }}>
                        <button type="button" onClick={() => loadScenario(scenario.scenario_id)}>Load</button>
                        {user.role === 'admin' && <button type="button" onClick={() => toggleSoa(scenario)}>
                            {scenario.is_soa ? "Remove SOTA" : "Publish as SOTA"}
                        </button>}
                        {scenario.can_delete && <button type="button" onClick={() => deleteScenario(scenario.scenario_id)}>Delete</button>}
                    </div>
                </div>
            ))}
            <h3>Compare two saved scenarios</h3>
            <div style={{ display: "flex", gap: 8, flexWrap: "wrap" }}>
                <select aria-label="First scenario" value={compareA} onChange={e => setCompareA(e.target.value)}>
                    <option value="">First scenario</option>
                    {savedScenarios.map(s => <option key={s.scenario_id} value={s.scenario_id}>{s.scenario_name}</option>)}
                </select>
                <select aria-label="Second scenario" value={compareB} onChange={e => setCompareB(e.target.value)}>
                    <option value="">Second scenario</option>
                    {savedScenarios.map(s => <option key={s.scenario_id} value={s.scenario_id}>{s.scenario_name}</option>)}
                </select>
                <button type="button" onClick={compareScenarios}>Compare</button>
            </div>
             {comparison && (
                 <div className="scenario-total-charts" style={{ display: "grid", gridTemplateColumns: "repeat(auto-fit, minmax(260px, 1fr))", gap: 16, marginTop: 18 }}>
                     {totalComparisonMetrics.map(metric => (
                         <div key={metric.key} className="chart-card" style={{ minWidth: 0 }}>
                             <h4>{metric.title}</h4>
                             <ResponsiveContainer width="100%" height={260}>
                                 <BarChart data={metric.data} margin={{ top: 12, right: 12, left: 8, bottom: 42 }}>
                                     <CartesianGrid strokeDasharray="3 3" />
                                     <XAxis dataKey="name" interval={0} angle={-25} textAnchor="end" height={60} />
                                     <YAxis width={75} tickFormatter={value => Number(value).toLocaleString(undefined, { notation: "compact", maximumFractionDigits: 1 })} />
                                     <Tooltip formatter={value => [Number(value).toLocaleString(undefined, { maximumFractionDigits: 2 }), metric.title]} />
                                     <Bar dataKey="value" name={metric.title} fill="#1f4b8f" maxBarSize={85} />
                                 </BarChart>
                             </ResponsiveContainer>
                         </div>
                     ))}
                 </div>
             )}
            {comparison && <div className="results-table-wrapper" style={{ marginTop: 12 }}>
                <table className="results-table">
                    <thead><tr><th>Metric</th>{comparison.map(s => <th key={s.scenario_id}>{s.scenario_name}</th>)}</tr></thead>
                    <tbody>
                        {[
                            ["Throughput (cells/day)", "throughput"],
                            ["Total cost", "total_cost"],
                            ["Total energy", "total_energy"],
                            ["Total carbon", "total_carbon"],
                        ].map(([label, key]) => <tr key={key}><td>{label}</td>
                            {comparison.map(s => <td key={s.scenario_id}>{Number(s[key] ?? 0).toLocaleString(undefined, { maximumFractionDigits: 2 })}</td>)}
                        </tr>)}
                        <tr><td>Machines</td>{comparison.map(s => <td key={s.scenario_id}>{s.result_json?.overall?.machines ?? "—"}</td>)}</tr>
                        <tr><td>Operators</td>{comparison.map(s => <td key={s.scenario_id}>{s.result_json?.overall?.operators ?? "—"}</td>)}</tr>
                    </tbody>
                </table>
            </div>}
        </section>

    </div>

</div>



</div>

);

}