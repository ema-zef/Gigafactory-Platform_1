import RecordConfigurator from "./RecordConfigurator";

const groups = [
  { id: "general", name: "Equipment Identity", description: "Machine identity, manufacturer and description" },
  { id: "process", name: "Process & Technology", description: "Process category, technology and operating mode" },
  { id: "capacity", name: "Capacity & Timing", description: "Cycle time, batches, uptime and throughput" },
  { id: "utilities", name: "Energy & Utilities", description: "Electricity, gas and utility consumption" },
  { id: "economics", name: "Costs & Resources", description: "Investment, floor space, labour and operating costs" },
];
function groupFor(key) {
  const n = key.toLowerCase();
  if (/process|technology|category|environment|mode|unit/.test(n)) return "process";
  if (/capacity|cycle|batch|speed|throughput|uptime|availability|time|duration|shift|yield/.test(n)) return "capacity";
  if (/energy|electric|gas|power|water|heat|consumption|co2|emission/.test(n)) return "utilities";
  if (/cost|price|eur|capex|opex|overhead|operator|labour|labor|floor|area|space|wage/.test(n)) return "economics";
  if (/equipment|machine|manufacturer|model|name|description|code|supplier/.test(n)) return "general";
  return "other";
}
export default function EquipmentManager() {
  return <RecordConfigurator endpoint="equipment" title="Equipment Configurator"
    subtitle="Select equipment and configure process, capacity, utilities and costs."
    groups={groups} groupFor={groupFor} idField="id"
    nameFor={r => [r.technology_name || r.equipment_name || r.machine_name || r.name || r.process || `Equipment ${r.id}`, r.process && (r.technology_name || r.equipment_name || r.machine_name || r.name) ? r.process : null].filter(Boolean).join(" · ")} />;
}
