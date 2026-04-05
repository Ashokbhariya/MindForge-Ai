import React, { useEffect, useState, useRef } from "react";
import { Link, useNavigate } from "react-router-dom";

const SERVICES = [
  { label: "🗺️ Roadmap",           to: "/roadmap"            },
  { label: "📚 Learn & Quiz",       to: "/learn&quiz"         },
  { label: "🔁 Recall Card",        to: "/recallcard"         },
  { label: "🧩 Confusion Detector", to: "/confusion-detector" },
  { label: "📊 Progress Card",      to: "/progresscard"       },
];

export default function DashNav() {
  const navigate = useNavigate();
  const [user, setUser]               = useState(null);
  const [userDropdown, setUserDropdown] = useState(false);
  const [servicesOpen, setServicesOpen] = useState(false);
  const userRef     = useRef(null);
  const servicesRef = useRef(null);

  useEffect(() => {
    try {
      const stored = localStorage.getItem("user");
      if (stored) setUser(JSON.parse(stored));
    } catch { /* ignore */ }
  }, []);

  // Close dropdowns when clicking outside
  useEffect(() => {
    const handler = (e) => {
      if (userRef.current && !userRef.current.contains(e.target))
        setUserDropdown(false);
      if (servicesRef.current && !servicesRef.current.contains(e.target))
        setServicesOpen(false);
    };
    document.addEventListener("mousedown", handler);
    return () => document.removeEventListener("mousedown", handler);
  }, []);

  const handleLogout = () => {
    localStorage.clear();
    sessionStorage.clear();
    window.location.href = "/";
  };

  const initial = user?.name?.charAt(0)?.toUpperCase() || "U";

  return (
    <nav className="flex items-center justify-between px-8 py-4 bg-white shadow-sm">
      {/* Logo */}
      <Link to="/" className="flex items-center gap-2">
        <div className="w-9 h-9 rounded-full bg-primary flex items-center justify-center">
          <span className="text-white font-bold text-sm">M</span>
        </div>
        <span className="text-xl font-bold text-primary">MindForgeAI</span>
      </Link>

      <div className="flex items-center gap-4">

        {/* ── Services dropdown ── */}
        <div className="relative" ref={servicesRef}>
          <button
            onClick={() => setServicesOpen((v) => !v)}
            className="px-4 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition flex items-center gap-1"
          >
            Services
            <svg
              className={`w-3 h-3 transition-transform ${servicesOpen ? "rotate-180" : ""}`}
              fill="none" stroke="currentColor" strokeWidth="2.5"
              viewBox="0 0 24 24"
            >
              <path strokeLinecap="round" strokeLinejoin="round" d="M19 9l-7 7-7-7" />
            </svg>
          </button>

          {servicesOpen && (
            <div className="absolute left-0 mt-2 w-52 bg-white border border-gray-200 rounded-xl shadow-lg z-50 overflow-hidden">
              {SERVICES.map((s) => (
                <Link
                  key={s.to}
                  to={s.to}
                  onClick={() => setServicesOpen(false)}
                  className="block px-4 py-3 text-sm text-gray-700 font-medium hover:bg-blue-50 hover:text-primary transition"
                >
                  {s.label}
                </Link>
              ))}
            </div>
          )}
        </div>

        {/* Dashboard button */}
        <Link
          to="/dashboard"
          className="px-4 py-2 bg-primary text-white rounded-lg text-sm font-medium hover:bg-blue-700 transition"
        >
          Dashboard
        </Link>

        {/* ── User avatar + dropdown ── */}
        <div className="relative" ref={userRef}>
          <button
            onClick={() => setUserDropdown((v) => !v)}
            className="w-10 h-10 rounded-full bg-primary text-white font-bold text-sm flex items-center justify-center hover:opacity-90 transition"
          >
            {initial}
          </button>

          {userDropdown && (
            <div className="absolute right-0 mt-2 w-56 bg-white border border-gray-200 rounded-xl shadow-lg z-50">
              <div className="flex items-center gap-3 px-4 py-3 border-b border-gray-100">
                <div className="w-9 h-9 rounded-full bg-primary text-white font-bold text-sm flex items-center justify-center flex-shrink-0">
                  {initial}
                </div>
                <div className="min-w-0">
                  <p className="font-semibold text-gray-800 text-sm truncate">
                    {user?.name || "User"}
                  </p>
                  <p className="text-xs text-gray-500 truncate">
                    {user?.email || ""}
                  </p>
                </div>
              </div>
              <button
                onClick={handleLogout}
                className="w-full text-left px-4 py-3 text-sm text-red-600 font-medium hover:bg-red-50 rounded-b-xl transition"
              >
                Logout
              </button>
            </div>
          )}
        </div>

      </div>
    </nav>
  );
}