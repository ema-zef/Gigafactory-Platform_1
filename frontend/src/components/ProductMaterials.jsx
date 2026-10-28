import { useLocation, useNavigate } from "react-router-dom";
import RecordConfigurator from "./RecordConfigurator";

const groups = [
  { id: "general", name: "Product & Material", description: "Material identity and associated product" },
  { id: "cathode", name: "Cathode Materials", description: "Cathode active material, additives, binder and collector" },
  { id: "anode", name: "Anode Materials", description: "Anode active material, additives, binder and collector" },
  { id: "assembly", name: "Assembly Materials", description: "Separator, electrolyte, housing and sealing" },
  { id: "prices", name: "Prices & Impacts", description: "Material prices, transport and environmental factors" },
];
function groupFor(key) {
  const n = key.toLowerCase();
  if (/productcode|product_code|materialcode|material_code|name|description|type|category/.test(n)) return "general";
  if (/cath|positive/.test(n)) return "cathode";
  if (/anode|negative/.test(n)) return "anode";
  if (/separator|electrolite|electrolyte|housing|sealing|assembly/.test(n)) return "assembly";
  if (/cost|price|eur|emission|carbon|transport|co2|rate/.test(n)) return "prices";
  return "other";
}
export default function ProductMaterialManager() {
  const location = useLocation();
  const navigate = useNavigate();
  const productCode = location.state?.requireMaterial ? String(location.state?.productCode || "").trim() : "";
  return <RecordConfigurator endpoint="product_material" title="Product Material Configurator"
    subtitle="Choose a product material record and edit its properties by category."
    groups={groups} groupFor={groupFor} idField="id" preferredId={productCode}
    initialValues={() => productCode ? { productcode: productCode } : {}}
    nameFor={r => [r.productcode || r.product_code || "Product", [r.materialcode, r.material_code, r.materialname, r.material_name].find(v => v != null && String(v).trim() && String(v).toLowerCase() !== "undefined") || `Material ${r.id ?? r.row_id ?? "record"}`].join(" · ")}
    onCreated={() => { if (productCode) navigate("/materials", { replace: true }); }}
    onSaved={() => { if (productCode) navigate("/materials", { replace: true }); }} />;
}
