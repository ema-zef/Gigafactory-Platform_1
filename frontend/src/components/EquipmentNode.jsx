import { useState } from "react";
import { Handle, Position } from "reactflow";

export default function EquipmentNode({ data }) {

  const [showData, setShowData] =
    useState(false);

  const equipment =
    data.equipment || {};

  return (
    <div
      style={{
        padding: "12px",
        border: "2px solid #555",
        borderRadius: "8px",
        background: "white",
        minWidth: "250px",
        maxWidth: "350px",
        boxShadow:
          "0 2px 6px rgba(0,0,0,0.2)",
      }}
    >

      <Handle
        type="target"
        position={Position.Left}
      />

      <div
        style={{
          display: "flex",
          justifyContent:
            "space-between",
          alignItems: "center",
          marginBottom: "8px",
        }}
      >

        <strong>
          {equipment.technology_name ||
            "Equipment"}
        </strong>

        <button
          onClick={(e) => {
            e.stopPropagation();

            if (data.deleteNode) {
              data.deleteNode(
                data.id
              );
            }
          }}
          style={{
            background: "#d9534f",
            color: "white",
            border: "none",
            borderRadius: "4px",
            cursor: "pointer",
          }}
        >
          X
        </button>

      </div>

      <div>
        <strong>Process:</strong>{" "}
        {equipment.process}
      </div>

      <div>
        <strong>Capacity:</strong>{" "}
        {equipment.capacity}
      </div>

      <button
        style={{
          marginTop: "10px",
          width: "100%",
        }}
        onClick={(e) => {
          e.stopPropagation();
          setShowData(!showData);
        }}
      >
        {showData
          ? "Hide Data"
          : "View Data"}
      </button>

      {showData && (

        <div
          style={{
            marginTop: "10px",
            maxHeight: "250px",
            overflowY: "auto",
            borderTop:
              "1px solid #ddd",
            paddingTop: "8px",
            fontSize: "12px",
          }}
        >

          {Object.entries(
            equipment
          ).map(
            ([key, value]) => (

              <div
                key={key}
                style={{
                  marginBottom:
                    "3px",
                }}
              >
                <strong>
                  {key}
                </strong>
                :
                {" "}
                {String(value)}
              </div>

            )
          )}

        </div>

      )}

      <Handle
        type="source"
        position={Position.Right}
      />

    </div>
  );
}