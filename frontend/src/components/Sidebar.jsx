import "./Sidebar.css";

import { NavLink } from "react-router-dom";

import {
    Home,
    Database,
    Package,
    Factory,
    Boxes,
    Route,
    BarChart3,
    Settings,
    ChevronLeft
} from "lucide-react";

const menu = [

    {
         icon: Home, label: "Dashboard", path: "/" 
		
    },

    {
        icon: Database, label: "Equipment Database", path: "/equipment"
        
    },

    {
        icon: Package, label: "Product Configuration", path: "/product-configuration"
        
    },

    {
        icon: Factory, label: "Production Configuration", path: "/production-configuration" 
        
    },

    {
        icon: Boxes, label: "Product Materials", path: "/materials"

    },

    {
        icon: Route, label: "Route Builder", path: "/route-builder"

    },

    {
        icon: BarChart3, label: "Analytics", path: "/analytics"
        
    },

    {
        icon: Settings, label: "Settings", path: "/settings"
        
    }

];

export default function Sidebar({

    open,
    closeSidebar

}) {

    return (

        <aside

            className={`sidebar ${open ? "open" : ""}`}

        >

            {/* =======================================
                HEADER
            ======================================== */}

            <div className="sidebar-header">

                <h2>

                    Gigafactory

                </h2>

                <button

                    className="collapse-button"

                    onClick={closeSidebar}

                >

                    <ChevronLeft size={18}/>

                </button>

            </div>

            {/* =======================================
                MENU
            ======================================== */}

            <nav className="sidebar-menu">

                {

                    menu.map(

                        (

                            item,

                            index

                        ) => {

                            const Icon = item.icon;

                            return (

                                <NavLink

    key={index}

    to={item.path}

    className={({ isActive }) =>

        isActive

            ? "sidebar-item active"

            : "sidebar-item"

    }

    onClick={closeSidebar}

>

    <Icon size={20} />

    <span>

        {item.label}

    </span>

</NavLink>

                            );

                        }

                    )

                }

            </nav>

            {/* =======================================
                FOOTER
            ======================================== */}

            <div className="sidebar-footer">

                Version 1.0

            </div>

        </aside>

    );

}