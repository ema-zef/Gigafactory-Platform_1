import { useState, useEffect } from "react";
import axios from "axios";

import "./ManufacturingRouteBuilder.css";
import SimulationResultsPanel from "./SimulationResultsPanel";

export default function ManufacturingRouteBuilder({

    plantOptions,
    productOptions,

    selectedPlant,
    setSelectedPlant,

    selectedProduct,
    setSelectedProduct

}) {

    const API =
        import.meta.env.VITE_API_URL ||
        "http://localhost:8000";

    // -----------------------------------------------------
    // Equipment
    // -----------------------------------------------------

    const [equipmentOptions, setEquipmentOptions] = useState([]);

    useEffect(() => {

        axios

            .get(`${API}/equipment/options`)

            .then(res => {

                setEquipmentOptions(res.data);

            })

            .catch(err => {

                console.error(
                    "Equipment load failed",
                    err
                );

            });

    }, []);

    // -----------------------------------------------------
    // Simulation Results
    // -----------------------------------------------------

    const [simulationResults, setSimulationResults] =
        useState([]);

    // -----------------------------------------------------
    // Route Step Template
    // -----------------------------------------------------

    const createStep = () => ({

        equipment_id: null,

        technology_id: null,

        technology_name: "",

        process: "",

        process_category: "",

        quality_rate: ""

    });

    // -----------------------------------------------------
    // Initial Routes
    // -----------------------------------------------------

    const [cathodeSteps, setCathodeSteps] =
        useState([

            createStep(),

            createStep(),

            createStep(),

            createStep(),

            createStep()

        ]);

    const [anodeSteps, setAnodeSteps] =
        useState([

            createStep(),

            createStep(),

            createStep(),

            createStep(),

            createStep()

        ]);

    const [assemblySteps, setAssemblySteps] =
        useState([

            createStep(),

            createStep(),

            createStep(),

            createStep()

        ]);

    // -----------------------------------------------------
    // Route Helpers
    // -----------------------------------------------------

    const updateStep = (

        index,
        field,
        value,
        steps,
        setSteps

    ) => {

        const copy = [...steps];

        copy[index] = {

            ...copy[index],

            [field]: value

        };

        setSteps(copy);

    };

    const addStep = (

        steps,
        setSteps

    ) => {

        setSteps([

            ...steps,

            createStep()

        ]);

    };

    const deleteStep = (

        index,
        steps,
        setSteps

    ) => {

        const copy = [...steps];

        copy.splice(index, 1);

        setSteps(copy);

    };

    const moveStepUp = (

        index,
        steps,
        setSteps

    ) => {

        if (index === 0) return;

        const copy = [...steps];

        [

            copy[index - 1],

            copy[index]

        ] = [

            copy[index],

            copy[index - 1]

        ];

        setSteps(copy);

    };

    const moveStepDown = (

        index,
        steps,
        setSteps

    ) => {

        if (index >= steps.length - 1) return;

        const copy = [...steps];

        [

            copy[index],

            copy[index + 1]

        ] = [

            copy[index + 1],

            copy[index]

        ];

        setSteps(copy);

    };

    // -----------------------------------------------------
    // Save Route
    // -----------------------------------------------------

    const saveRoute = async () => {

        try {

            await axios.post(

                `${API}/manufacturing_route`,

                {

                    plant: selectedPlant,

                    product: selectedProduct,

                    cathode: cathodeSteps,

                    anode: anodeSteps,

                    assembly: assemblySteps

                }

            );

            alert("Manufacturing Route saved.");

        }

        catch (err) {

            console.error(err);

            alert("Unable to save route.");

        }

    };

    // -----------------------------------------------------
    // Run Simulation
    // -----------------------------------------------------

    const handleRunSimulation = async () => {

        try {

            const response = await axios.post(

                `${API}/simulation/run`,

                {

                    plant_code: selectedPlant,

                    product_code: selectedProduct,

                    cathode_route: cathodeSteps,

                    anode_route: anodeSteps,

                    assembly_route: assemblySteps

                }

            );

            console.log(
    JSON.stringify(
        response.data,
        null,
        2
    )
);

            setSimulationResults(response.data);

        }

        catch (err) {

            console.error(err);

        }

    };

const renderTable = (

    title,

    steps,

    setSteps

) => (

    <div className="route-card">

        <h2 className="route-title">

            {title}

        </h2>

        <div className="table-wrapper">

            <table className="route-table">

                <thead>

                    <tr>

                        <th className="step-col">

                            Step

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

                        <tr key={index}>

                            <td>

                                {index + 1}

                            </td>

                            <td>

                                <select

                                    value={step.equipment_id || ""}

                                    onChange={(e) => {

                                        const selected =

                                            equipmentOptions.find(

                                                eq =>

                                                    eq.id ===

                                                    Number(e.target.value)

                                            );

                                        if (!selected) return;

                                        const copy = [...steps];

                                        copy[index] = {

                                            ...copy[index],

                                            equipment_id:

                                                selected.id,

                                            technology_id:

                                                selected.id,

                                            technology_name:

                                                selected.technology_name,

                                            process:

                                                selected.process,

                                            process_category:

                                                selected.process_category,

                                            quality_rate:

                                                selected.quality_rate

                                        };

                                        setSteps(copy);

                                    }}

                                >

                                    <option value="">

                                        Select Equipment

                                    </option>

                                    {equipmentOptions.map(eq => (

                                        <option

                                            key={eq.id}

                                            value={eq.id}

                                        >

                                            {eq.technology_name}

                                        </option>

                                    ))}

                                </select>

                            </td>

                            <td>

                                <input

                                    value={step.process || ""}

                                    readOnly

                                />

                            </td>

                            <td>

                                <input

                                    value={step.process_category || ""}

                                    readOnly

                                />

                            </td>

                            <td>

                                <input

                                    value={step.quality_rate || ""}

                                    readOnly

                                />

                            </td>

                            <td>

                                <div className="route-actions-cell">

                                    <button

                                        onClick={() =>

                                            moveStepUp(

                                                index,

                                                steps,

                                                setSteps

                                            )

                                        }

                                    >

                                        ↑

                                    </button>

                                    <button

                                        onClick={() =>

                                            moveStepDown(

                                                index,

                                                steps,

                                                setSteps

                                            )

                                        }

                                    >

                                        ↓

                                    </button>

                                    <button

                                        onClick={() =>

                                            deleteStep(

                                                index,

                                                steps,

                                                setSteps

                                            )

                                        }

                                    >

                                        ✖

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

    return (

<div className="route-builder">

    {/* ==============================
        PAGE HEADER
    ============================== */}

    <div className="builder-page-header">

        <div className="builder-page-title">

            <h1>

                Route Builder

            </h1>

            <p>

                Design, simulate and optimize your battery cell production.

            </p>

        </div>

        <div className="builder-page-status">

            <span className="status-dot"></span>

            Backend Connected

        </div>

        <div className="builder-page-actions">

            <button
                className="reset-route-btn"
                onClick={() => {

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

                }}
            >

                Reset

            </button>

            <button

                className="save-route-btn"

                onClick={saveRoute}

            >

                💾 Save Route

            </button>

            <button

                className="run-simulation-btn"

                onClick={handleRunSimulation}

            >

                ▶ Run Simulation

            </button>

        </div>

    </div>



</div>

);

}