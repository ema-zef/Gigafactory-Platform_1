import React from "react";
import ReactFlow from "reactflow";
import "reactflow/dist/style.css";
import EquipmentPalette from "./EquipmentPalette";

const nodes = [
  {
    id: "factory",
    position: { x: 250, y: 50 },
    data: { label: "Gigafactory" },
    type: "input",
  },

  {
    id: "mixing",
    position: { x: 100, y: 180 },
    data: { label: "Mixing" },
  },

  {
    id: "coating",
    position: { x: 400, y: 180 },
    data: { label: "Coating" },
  },
];

const edges = [
  {
    id: "e1",
    source: "factory",
    target: "mixing",
  },
  {
    id: "e2",
    source: "factory",
    target: "coating",
  },
];

export default function GigafactoryFlow() {
  return (
    <div style={{ width: "100%", height: "600px" }}>
      <ReactFlow nodes={nodes} edges={edges} fitView />
    </div>
  );
}

const onDrop = (event) => {

  event.preventDefault();

  const equipment =
    JSON.parse(
      event.dataTransfer.getData(
        "equipment"
      )
    );

  const position =
    screenToFlowPosition({
      x: event.clientX,
      y: event.clientY
    });

  const newNode = {
    id: crypto.randomUUID(),
    type: "default",
    position,
    data: {
      label:
        equipment.technology_name
    }
  };

  setNodes(nds => [
    ...nds,
    newNode
  ]);
};