import RecordConfigurator from "./RecordConfigurator";

const groups = [
  { id: "general", name: "General & Plant", description: "Plant identity and production scenario" },
  { id: "schedule", name: "Working Calendar", description: "Days, shifts and available working time" },
  { id: "targets", name: "Production Targets", description: "Annual output, capacity and production goals" },
  { id: "costs", name: "Costs & Assumptions", description: "Operating and economic assumptions" },
];
function groupFor(key) {
  const n = key.toLowerCase();
  if (/day|shift|hour|minute|week|calendar|uptime|availability|time/.test(n)) return "schedule";
  if (/output|capacity|volume|target|demand|yield|annual|cells|kwh/.test(n)) return "targets";
  if (/cost|price|rate|eur|salary|wage|overhead|labour|labor/.test(n)) return "costs";
  if (/plant|production|product|code|name|description|scenario/.test(n)) return "general";
  return "other";
}
export default function ProductionConfigurationManager() {
  return <RecordConfigurator endpoint="production_configuration" title="Production Configurator"
    subtitle="Configure production schedules, output targets and operating assumptions."
    groups={groups} groupFor={groupFor} idField="id"
    nameFor={r => [r.plantcode || r.plant_code || r.plant || r.productioncode || r.production_code || r.name || `Production ${r.id}`, r.productcode || r.product_code].filter(Boolean).join(" · ")} />;
}
