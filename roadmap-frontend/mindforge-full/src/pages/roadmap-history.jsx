import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Navbar from "../components/DashNav";
import Footer from "../components/Footer";

const BASE_URL = "http://127.0.0.1:8000";

const LEVEL_COLORS = {
  beginner:     "bg-green-100 text-green-700",
  intermediate: "bg-yellow-100 text-yellow-700",
  advanced:     "bg-red-100 text-red-700",
};

export default function RoadmapHistory() {
  const navigate = useNavigate();

  const [history, setHistory]         = useState([]);
  const [filtered, setFiltered]       = useState([]);
  const [loading, setLoading]         = useState(true);
  const [error, setError]             = useState(null);
  const [search, setSearch]           = useState("");
  const [levelFilter, setLevelFilter] = useState("all");
  const [expanded, setExpanded]       = useState({});   // { roadmapId: bool }

  // ── Fetch history ──────────────────────────────────────────────
  useEffect(() => {
    let userId = null;
    try {
      const stored = localStorage.getItem("user");
      if (stored) userId = JSON.parse(stored)?.id || null;
    } catch { /* ignore */ }

    if (!userId) {
      setError("Please log in to view your roadmap history.");
      setLoading(false);
      return;
    }

    fetch(`${BASE_URL}/api/roadmap/user/${userId}/history`)
      .then((res) => {
        if (!res.ok) throw new Error("Failed to fetch history");
        return res.json();
      })
      .then((data) => {
        const list = Array.isArray(data) ? data : data.roadmaps || [];
        setHistory(list);
        setFiltered(list);
      })
      .catch((err) => {
        console.error(err);
        setError("Could not load roadmap history. Make sure the backend is running.");
      })
      .finally(() => setLoading(false));
  }, []);

  // ── Filter whenever search or level changes ────────────────────
  useEffect(() => {
    let result = history;
    if (levelFilter !== "all") {
      result = result.filter(
        (r) => (r.level || "beginner").toLowerCase() === levelFilter
      );
    }
    if (search.trim()) {
      const q = search.trim().toLowerCase();
      result = result.filter((r) => r.topic?.toLowerCase().includes(q));
    }
    setFiltered(result);
  }, [search, levelFilter, history]);

  const toggleExpand = (id) =>
    setExpanded((prev) => ({ ...prev, [id]: !prev[id] }));

  // Navigate to roadmap page with the topic pre-filled
  const handleReopen = (roadmap) => {
    navigate("/roadmap", {
      state: { prefill: roadmap.topic, level: roadmap.level },
    });
  };

  // ── Render ─────────────────────────────────────────────────────
  return (
    <div className="min-h-screen bg-[#f9fafe] flex flex-col">
      <Navbar />

      <main className="flex-1 px-6 py-10 max-w-4xl mx-auto w-full">

        {/* Page title */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-gray-800">Roadmap History</h1>
          <p className="text-gray-500 mt-1">
            All roadmaps you've generated — pick up where you left off.
          </p>
        </div>

        {/* Search + filter bar */}
        <div className="flex flex-col sm:flex-row gap-3 mb-6">
          <input
            type="text"
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            placeholder="Search by topic…"
            className="flex-1 px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm"
          />
          <select
            value={levelFilter}
            onChange={(e) => setLevelFilter(e.target.value)}
            className="px-4 py-2 rounded-lg border border-gray-300 focus:outline-none focus:ring-2 focus:ring-blue-500 text-sm bg-white"
          >
            <option value="all">All Levels</option>
            <option value="beginner">Beginner</option>
            <option value="intermediate">Intermediate</option>
            <option value="advanced">Advanced</option>
          </select>
        </div>

        {/* Loading spinner */}
        {loading && (
          <div className="flex justify-center mt-16">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
          </div>
        )}

        {/* Error */}
        {error && (
          <div className="bg-red-50 border border-red-200 text-red-600 rounded-lg p-4 mt-4 text-sm">
            {error}
          </div>
        )}

        {/* Empty state */}
        {!loading && !error && filtered.length === 0 && (
          <div className="bg-white rounded-xl shadow p-10 text-center text-gray-500 mt-4">
            {history.length === 0 ? (
              <>
                <p className="text-lg mb-4">No roadmaps yet.</p>
                <button
                  onClick={() => navigate("/roadmap")}
                  className="bg-blue-600 text-white px-6 py-2 rounded-lg hover:bg-blue-700 transition"
                >
                  Generate your first roadmap
                </button>
              </>
            ) : (
              <p>No roadmaps match your search.</p>
            )}
          </div>
        )}

        {/* Roadmap cards */}
        <div className="space-y-4">
          {filtered.map((entry) => {
            const isOpen   = !!expanded[entry.id];
            const level    = (entry.level || "beginner").toLowerCase();
            const levelCls = LEVEL_COLORS[level] || "bg-gray-100 text-gray-600";
            const date     = entry.created_at
              ? new Date(entry.created_at).toLocaleDateString(undefined, {
                  year: "numeric", month: "short", day: "numeric",
                })
              : null;

            return (
              <div
                key={entry.id}
                className="bg-white rounded-xl shadow hover:shadow-md transition overflow-hidden"
              >
                {/* Card header */}
                <div className="p-5 flex items-start justify-between gap-4">
                  <div className="flex-1 min-w-0">
                    <div className="flex items-center gap-2 flex-wrap mb-1">
                      <h3 className="text-base font-semibold text-gray-800 truncate">
                        {entry.topic}
                      </h3>
                      <span
                        className={`text-xs px-2 py-0.5 rounded-full font-medium capitalize ${levelCls}`}
                      >
                        {level}
                      </span>
                    </div>
                    {entry.description && (
                      <p className="text-sm text-gray-500 line-clamp-2">
                        {entry.description}
                      </p>
                    )}
                    {date && (
                      <p className="text-xs text-gray-400 mt-1">{date}</p>
                    )}
                  </div>

                  {/* Action buttons */}
                  <div className="flex items-center gap-2 shrink-0">
                    {Array.isArray(entry.subtopics) && entry.subtopics.length > 0 && (
                      <button
                        onClick={() => toggleExpand(entry.id)}
                        className="text-xs text-blue-600 border border-blue-200 px-3 py-1.5 rounded-lg hover:bg-blue-50 transition"
                      >
                        {isOpen
                          ? "Hide"
                          : `Subtopics (${entry.subtopics.length})`}
                      </button>
                    )}
                    <button
                      onClick={() => handleReopen(entry)}
                      className="text-xs bg-blue-600 text-white px-3 py-1.5 rounded-lg hover:bg-blue-700 transition"
                    >
                      Open →
                    </button>
                  </div>
                </div>

                {/* Expandable subtopics panel */}
                {isOpen && Array.isArray(entry.subtopics) && (
                  <div className="border-t border-gray-100 px-5 py-4 bg-gray-50">
                    <p className="text-xs font-semibold text-gray-400 uppercase mb-3">
                      Subtopics
                    </p>
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-2">
                      {entry.subtopics.map((sub, i) => (
                        <div
                          key={i}
                          className="flex items-start gap-2 bg-white rounded-lg px-3 py-2 shadow-sm border border-gray-100"
                        >
                          <span className="mt-0.5 w-5 h-5 rounded-full bg-blue-100 text-blue-600 text-xs font-bold flex items-center justify-center shrink-0">
                            {i + 1}
                          </span>
                          <div>
                            <p className="text-sm font-medium text-gray-700">
                              {sub.title}
                            </p>
                            {sub.description && (
                              <p className="text-xs text-gray-500 mt-0.5 line-clamp-2">
                                {sub.description}
                              </p>
                            )}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>
                )}
              </div>
            );
          })}
        </div>

        {/* Count summary */}
        {!loading && !error && history.length > 0 && (
          <p className="text-xs text-gray-400 text-center mt-8">
            Showing {filtered.length} of {history.length} roadmap
            {history.length !== 1 ? "s" : ""}
          </p>
        )}
      </main>

      <Footer />
    </div>
  );
}