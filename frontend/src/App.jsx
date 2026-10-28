import { useState, useEffect } from "react";
import axios from "axios";

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
import Login from "./components/Login";

import logo1 from "./assets/logo1.png";
import logo2 from "./assets/logo2.png";

const API = import.meta.env.VITE_API_URL || 'http://localhost:8000';
// All existing components use axios; set a single session header for all of them.
function setSession(token) {
  if (token) axios.defaults.headers.common.Authorization = `Bearer ${token}`;
  else delete axios.defaults.headers.common.Authorization;
}
// Legacy edit forms submit the entire row; strip read-only metadata and PKs.
axios.interceptors.request.use(config => {
  const match = String(config.url || '').match(/\/(equipment|product_configuration|product_material|production_configuration)(?:\/(\d+))?$/);
  if (match && ['post','put'].includes((config.method || '').toLowerCase()) && config.data && typeof config.data === 'object') {
    const pk = {equipment:'id',product_configuration:'row_id',product_material:'seq',production_configuration:'id'}[match[1]];
    const { [pk]: _pk, owner_id: _owner, is_sota: _sota, read_only: _readonly, sota_line_type: _line, ...fields } = config.data;
    config.data = fields;
  }
  return config;
});
export default function App() {
    const [user, setUser] = useState(null);
    const [checkingAuth, setCheckingAuth] = useState(true);
    useEffect(() => {
      const token = sessionStorage.getItem('app_access_token');
      if (!token) { setCheckingAuth(false); return; }
      setSession(token);
      axios.get(`${API}/me`).then(({data}) => setUser(data)).catch(() => {
        sessionStorage.removeItem('app_access_token'); setSession(null);
      }).finally(() => setCheckingAuth(false));
    }, []);
    function login(token, account) {
      sessionStorage.setItem('app_access_token', token); setSession(token); setUser(account);
    }
    function logout() {
      for (const key of Object.keys(sessionStorage)) if (key.startsWith('sota:')) sessionStorage.removeItem(key);
      sessionStorage.removeItem('app_access_token'); setSession(null); setUser(null);
    }


    const [sidebarOpen, setSidebarOpen] = useState(false);
	
	const [backendConnected, setBackendConnected] = useState(false);
	
	    useEffect(() => {

        async function checkBackend() {

            try {

                await axios.get(
                    `${import.meta.env.VITE_API_URL}/health`
                );

                setBackendConnected(true);

            }

            catch {

                setBackendConnected(false);

            }

        }

        checkBackend();

        const timer = setInterval(checkBackend, 5000);

        return () => clearInterval(timer);

    }, []);

    if (checkingAuth) return <p style={{padding:24}}>Checking session…</p>;
    if (!user) return <Login onLogin={login} />;
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

    {/* ================= LEFT ================= */}

    <div className="header-left">

        <button
            className="menu-button"
            onClick={() => setSidebarOpen(!sidebarOpen)}
        >
            ☰
        </button>

        <img
            src={logo1}
            alt="Logo 1"
            className="brand-logo logo-next"
        />

        <img
            src={logo2}
            alt="Logo 2"
            className="brand-logo logo-ut"
        />

    </div>

    {/* ================= CENTER ================= */}

<div className="header-center">

    <div
        className={`backend-status ${
            backendConnected ? "connected" : "disconnected"
        }`}
    >

        <span className="status-dot"></span>

        {backendConnected
            ? "Backend Connected"
            : "Connecting..."}

    </div>

</div>

    {/* ================= RIGHT ================= */}

    <div className="header-right">

        <span style={{marginRight:12}}>{user.username} ({user.role})</span>
        <button type="button" onClick={logout}>Log out</button>

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
                                    <ManufacturingRouteBuilder user={user} />
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