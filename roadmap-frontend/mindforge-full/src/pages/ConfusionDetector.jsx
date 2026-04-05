import React, { useState, useEffect } from "react";
import { useLocation } from "react-router-dom";
import Navbar from "../components/DashNav";
import Footer from "../components/Footer";

const BASE_URL = "http://127.0.0.1:8000";

const getUserId = () => {
  try {
    const user = JSON.parse(localStorage.getItem("user") || "{}");
    return user.id || user.user_id || null;
  } catch {
    return null;
  }
};

export default function ConfusionDetector() {
  const location = useLocation();
  const weakTopicsFromQuiz = location.state?.weakTopics  || [];
  const scoreFromQuiz      = location.state?.score       ?? null;
  const totalFromQuiz      = location.state?.total       ?? null;
  const percentageFromQuiz = location.state?.percentage  ?? null;

  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    const userId = getUserId();
    if (!userId) return;
    setLoading(true);

    // FIX: Use /api/quiz/confusion-topics which is where the backend
    // now saves confusion signals after every quiz submission.
    // The old /confusion-signals/{userId} endpoint uses different data.
    fetch(`${BASE_URL}/api/quiz/confusion-topics?user_id=${userId}`)
      .then((res) => res.json())
      .then((data) => setSignals(Array.isArray(data) ? data : []))
      .catch((err) => console.error("Error fetching confusion signals:", err))
      .finally(() => setLoading(false));
  }, []);

  const uniqueTopics = [...new Set(weakTopicsFromQuiz)];

  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary to-white text-dark flex flex-col">
      <Navbar />

      <main className="flex-1 px-6 py-16 max-w-5xl mx-auto">
        <h2 className="text-3xl font-bold text-primary mb-6 text-center">
          Confusion Detector
        </h2>

        {scoreFromQuiz !== null && (
          <div className="bg-blue-50 border border-blue-200 p-4 rounded text-blue-900 mb-6 text-center">
            <p className="text-xl font-bold">
              Your Score: {scoreFromQuiz}
              {totalFromQuiz      !== null ? ` / ${totalFromQuiz}`                   : ""}
              {percentageFromQuiz !== null ? ` (${Math.round(percentageFromQuiz)}%)` : ""}
            </p>
          </div>
        )}

        {uniqueTopics.length > 0 && (
          <div className="bg-yellow-100 border border-yellow-300 p-4 rounded text-yellow-800 mb-6">
            <p className="font-semibold mb-2">You are struggling with:</p>
            <ul className="list-disc list-inside">
              {uniqueTopics.map((topic, idx) => (
                <li key={idx}>{topic}</li>
              ))}
            </ul>
            <p className="mt-2">Let us work on them.</p>
          </div>
        )}

        {loading ? (
          <p className="text-center text-gray-600">Loading confusion signals...</p>
        ) : signals.length > 0 ? (
          <ul className="bg-white p-6 rounded-xl shadow-lg space-y-2">
            {signals.map((sig, idx) => (
              <li key={idx} className="border-b last:border-none py-3 text-gray-800">
                <span className="font-semibold text-red-600">{sig.topic}</span>
                {sig.message && (
                  <p className="text-sm text-gray-600 mt-1">{sig.message}</p>
                )}
              </li>
            ))}
          </ul>
        ) : (
          <p className="text-gray-700 text-center">
            {uniqueTopics.length === 0
              ? "No confusion signals found."
              : "Focus on these weak points."}
          </p>
        )}
      </main>

      <Footer />
    </div>
  );
}