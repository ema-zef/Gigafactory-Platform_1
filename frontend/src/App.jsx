import { useState } from "react";

import {
    BrowserRouter,
    Routes,
    Route,
    Navigate
} from "react-router-dom";

import "./App.css";

import Sidebar from "./components/Sidebar";

import ManufacturingRouteBuilder from "./components/ManufacturingRouteBuilder";
import EquipmentDatabase from "./components/EquipmentDatabase";
import ProductConfiguration from "./components/ProductConfiguration";
import ProductionConfiguration from "./components/ProductionConfiguration";
import ProductMaterials from "./components/ProductMaterials";
import Analytics from "./components/Analytics";
import Settings from "./components/Settings";

import logo1 from "./assets/logo1.png";
import logo2 from "./assets/logo2.png";

export default function App() {

    const [sidebarOpen, setSidebarOpen] = useState(false);

    return (

        <BrowserRouter>

            <div
                className={`app-shell ${
                    sidebarOpen ? "sidebar-open" : ""
                }`}
            >

                <Sidebar
                    open={sidebarOpen}
                    closeSidebar={() =>
                        setSidebarOpen(false)
                    }
                />

                <div className="app-content">

                    {/* ===================================
                        HEADER
                    ==================================== */}

                    <header className="app-header">

                        <div className="header-left">

                            <button
                                className="menu-button"
                                onClick={() =>
                                    setSidebarOpen(!sidebarOpen)
                                }
                                aria-label="Toggle Sidebar"
                            >
                                ☰
                            </button>

                            <div className="app-brand">

                                <img
                                    src={logo1}
                                    alt="Logo 1"
                                    className="brand-logo"
                                />

                                <img
                                    src={logo2}
                                    alt="Logo 2"
                                    className="brand-logo"
                                />

                            </div>

                        </div>

                    </header>

                    {/* ===================================
                        PAGE CONTENT
                    ==================================== */}

                    <main className="app-page">

                        <Routes>

                            <Route
                                path="/"
                                element={
                                    <Navigate
                                        to="/route-builder"
                                        replace
                                    />
                                }
                            />

                            <Route
                                path="/equipment"
                                element={
                                    <EquipmentDatabase />
                                }
                            />

                            <Route
                                path="/product-configuration"
                                element={
                                    <ProductConfiguration />
                                }
                            />

                            <Route
                                path="/production-configuration"
                                element={
                                    <ProductionConfiguration />
                                }
                            />

                            <Route
                                path="/materials"
                                element={
                                    <ProductMaterials />
                                }
                            />

                            <Route
                                path="/route-builder"
                                element={
                                    <ManufacturingRouteBuilder />
                                }
                            />

                            <Route
                                path="/analytics"
                                element={
                                    <Analytics />
                                }
                            />

                            <Route
                                path="/settings"
                                element={
                                    <Settings />
                                }
                            />

                        </Routes>

                    </main>

                </div>

            </div>

        </BrowserRouter>

    );

}