import { useState, useCallback } from "react";

import ReactFlow, {
Controls,
Background,
addEdge,
applyNodeChanges,
applyEdgeChanges,
} from "reactflow";

import "reactflow/dist/style.css";

import EquipmentNode from "./EquipmentNode";

const nodeTypes = {
  equipment: EquipmentNode
};

export default function EquipmentFlow() {

const [nodes, setNodes] = useState([]);

const [edges, setEdges] = useState([]);

const onNodesChange = useCallback(
(changes) => {
setNodes((nds) =>
applyNodeChanges(changes, nds)
);
},
[]
);

const onEdgesChange = useCallback(
(changes) => {
setEdges((eds) =>
applyEdgeChanges(changes, eds)
);
},
[]
);

const deleteNode = useCallback(
(id) => {


  setNodes((nds) =>
    nds.filter(
      (node) => node.id !== id
    )
  );

  setEdges((eds) =>
    eds.filter(
      (edge) =>
        edge.source !== id &&
        edge.target !== id
    )
  );

},
[]


);

const onConnect = useCallback(
(params) =>
setEdges((eds) =>
addEdge(params, eds)
),
[]
);

const onDragOver = useCallback(
(event) => {
event.preventDefault();


  event.dataTransfer.dropEffect =
    "move";
},
[]


);

const onDrop = useCallback(
(event) => {


  event.preventDefault();

  const equipmentData =
    event.dataTransfer.getData(
      "equipment"
    );

  if (!equipmentData) return;

  const equipment =
    JSON.parse(equipmentData);

  const bounds =
    event.currentTarget.getBoundingClientRect();

  const nodeId =
    crypto.randomUUID();

  const position = {
    x:
      event.clientX -
      bounds.left,
    y:
      event.clientY -
      bounds.top,
  };

  const newNode = {
    id: nodeId,

    type: "equipment",

    position,

    data: {
      id: nodeId,

      equipment,

      technology_name:
        equipment.technology_name,

      process:
        equipment.process,

      capacity:
        equipment.capacity,

      deleteNode,
    },
  };

  setNodes((nds) => [
    ...nds,
    newNode,
  ]);

},
[deleteNode]


);

return (


<div
  style={{
    width: "100%",
    height: "700px",
    border:
      "1px solid #ccc",
  }}
>

  <ReactFlow
    nodes={nodes}
    edges={edges}
    nodeTypes={nodeTypes}
    onNodesChange={
      onNodesChange
    }
    onEdgesChange={
      onEdgesChange
    }
    onConnect={onConnect}
    onDrop={onDrop}
    onDragOver={
      onDragOver
    }
    deleteKeyCode={[
      "Backspace",
      "Delete",
    ]}
    fitView
  >

    <Controls />

    <Background />

  </ReactFlow>

</div>


);
}
