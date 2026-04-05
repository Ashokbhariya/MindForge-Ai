import React, { useEffect, useState } from "react";
import Navbar from "../components/DashNav";
import Footer from "../components/Footer";
import { api } from "../services/api";

export default function ConfusionDetectorHistory() {
  const [confusions, setConfusions] = useState([]);
  const [loading, setLoading]       = useState(false);
  const [error, setError]           = useState("");

  const userId = (() => {
    try {
      return JSON.parse(localStorage.getItem("user") || "{}").id || null;
    } catch {
      return null;
    }
  })();

  useEffect(() => {
    if (!userId) {
      setError("No user found. Please log in.");
      return;
    }
    setLoading(true);
    api
      .getConfusionSignals(userId)
      .then((data) => setConfusions(Array.isArray(data) ? data : []))
      .catch((err) => {
        console.error("Confusion history error:", err);
        setError("Failed to load confusion history.");
      })
      .finally(() => setLoading(false));
  }, [userId]);

  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary to-white flex flex-col">
      <Navbar />
      <main className="flex-1 px-6 py-12 max-w-4xl mx-auto">
        <h2 className="text-3xl font-bold text-primary mb-6 text-center">
          Confusion Detector History
        </h2>

        {loading && <p className="text-center text-gray-600">Loading...</p>}

        {!loading && error && (
          <p className="text-center text-red-500">{error}</p>
        )}

        {!loading && !error && confusions.length === 0 && (
          <p className="text-center text-gray-600">No confusion history found.</p>
        )}

        {!loading && !error && confusions.map((item, idx) => (
          <div key={item.id || idx} className="bg-white p-4 rounded-xl shadow mb-4">
            <h4 className="text-sm font-semibold text-gray-600 mb-2">
              Topic: {item.topic || "N/A"}
            </h4>
            <p className="text-gray-800">{item.message || "Confusion signal detected"}</p>
          </div>
        ))}
      </main>
      <Footer />
    </div>
  );
}