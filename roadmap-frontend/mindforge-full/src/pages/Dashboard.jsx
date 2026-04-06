import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import Footer from "../components/Footer";

const BASE_URL = "https://mindforge-backend-gwj4.onrender.com";

const getUserId = () => {
  try {
    const user = JSON.parse(localStorage.getItem("user") || "{}");
    return user.id || user.user_id || null;
  } catch {
    return null;
  }
};

export default function Dashboard() {
  const navigate = useNavigate();

  const [user, setUser]                   = useState(null);
  const [latestRoadmap, setLatestRoadmap] = useState(null);
  const [quizResults, setQuizResults]     = useState([]);
  const [weakTopics, setWeakTopics]       = useState([]);
  const [loading, setLoading]             = useState(true);

  // Derived stats
  const avgScore = quizResults.length
    ? Math.round(
        quizResults.reduce((sum, r) => sum + (r.score / r.total_questions) * 100, 0) /
        quizResults.length
      )
    : 0;

  // Weak topics: from confusion signals + low-scoring quiz topics
  const weakFromQuiz = quizResults
    .filter((r) => Math.round((r.score / r.total_questions) * 100) < 70)
    .map((r) => r.topic);
  const uniqueWeak = [...new Set([...weakFromQuiz, ...weakTopics])].slice(0, 5);

  // Load user from localStorage
  useEffect(() => {
    try {
      const stored = localStorage.getItem("user");
      if (stored) setUser(JSON.parse(stored));
    } catch { /* ignore */ }
  }, []);

  // Fetch all user-specific data
  useEffect(() => {
    async function fetchAll() {
      setLoading(true);
      const userId = getUserId();

      // If no user logged in, stop loading and show empty state
      if (!userId) {
        setLoading(false);
        return;
      }

      try {
        // 1. Quiz results filtered by user_id
        const qRes = await fetch(`${BASE_URL}/api/quiz/results?user_id=${userId}`);
        if (qRes.ok) {
          const d = await qRes.json();
          setQuizResults(Array.isArray(d) ? d : []);
        }

        // 2. Confusion topics filtered by user_id
        const cRes = await fetch(`${BASE_URL}/api/quiz/confusion-topics?user_id=${userId}`);
        if (cRes.ok) {
          const d = await cRes.json();
          if (Array.isArray(d)) {
            setWeakTopics(d.map((s) => s.topic || "").filter(Boolean));
          }
        }

        // 3. Latest roadmap for this user
        const rRes = await fetch(`${BASE_URL}/api/roadmap/user/${userId}/latest`);
        if (rRes.ok) {
          const d = await rRes.json();
          if (d?.topic) setLatestRoadmap(d);
        }
      } catch (err) {
        console.error("Dashboard fetch error:", err);
      } finally {
        setLoading(false);
      }
    }
    fetchAll();
  }, []);

  const handleLogout = (e) => {
    e.preventDefault();
    localStorage.clear();
    sessionStorage.clear();
    window.location.href = "/";
  };

  return (
    <div className="min-h-screen flex flex-col font-inter">
      <div className="flex flex-1">

        {/* Sidebar */}
        <aside className="w-64 bg-secondary text-white flex flex-col py-8 px-6 space-y-6">
          <h2 className="text-2xl font-bold">MindForgeAI</h2>
          <nav className="flex flex-col space-y-4">
            <a href="/roadmap"            className="text-white hover:text-accent">Roadmap</a>
            <a href="/learn&quiz"         className="text-white hover:text-accent">Learn &amp; Quiz</a>
            <a href="/recallcard"         className="text-white hover:text-accent">Recall Card</a>
            <a href="/confusion-detector" className="text-white hover:text-accent">Confusion Detector</a>
            <a href="/progresscard"       className="text-white hover:text-accent">Progress Card</a>
            <a href="/" onClick={handleLogout} className="text-white hover:text-accent">Logout</a>
          </nav>
        </aside>

        {/* Main content */}
        <main className="flex-1 bg-[#f9fafe] p-10">

          {/* Header */}
          <div className="flex justify-between items-center mb-10">
            <div>
              <h1 className="text-3xl font-bold text-gray-800">
                Welcome{user?.name ? `, ${user.name}` : ""} 👋
              </h1>
              <p className="text-gray-500">Continue your learning journey</p>
            </div>
            {user?.name && (
              <div className="w-10 h-10 rounded-full bg-blue-600 text-white flex items-center justify-center font-bold text-lg">
                {user.name.charAt(0).toUpperCase()}
              </div>
            )}
          </div>

          {loading ? (
            <div className="flex items-center justify-center h-48">
              <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-blue-600" />
            </div>
          ) : (
            <>
              {/* Career goal banner */}
              {user?.career_goal && (
                <div className="bg-gradient-to-r from-blue-700 to-indigo-500 text-white p-6 rounded-xl shadow mb-8 flex items-center gap-5">
                  <div className="text-4xl">🎯</div>
                  <div>
                    <p className="text-sm font-semibold uppercase tracking-widest opacity-75 mb-1">
                      Your Career Goal
                    </p>
                    <p className="text-2xl font-bold">{user.career_goal}</p>
                    <p className="text-sm opacity-75 mt-1">
                      Every roadmap and quiz is bringing you closer to this.
                    </p>
                  </div>
                </div>
              )}

              {/* Continue course + quiz performance */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
                <div className="bg-[#1a213d] text-white p-6 rounded-lg md:col-span-2">
                  <h2 className="text-lg mb-2">
                    {latestRoadmap ? "Continue Learning" : "Start Learning"}
                  </h2>
                  <div className="flex items-center justify-between">
                    <div>
                      <h3 className="text-xl font-semibold">
                        {latestRoadmap?.topic || "Generate your first roadmap"}
                      </h3>
                      {latestRoadmap?.level && (
                        <p className="text-sm text-blue-300 mt-1 capitalize">
                          Level: {latestRoadmap.level}
                        </p>
                      )}
                    </div>
                    <button
                      onClick={() => navigate("/roadmap")}
                      className="bg-blue-600 px-4 py-2 text-white rounded-md hover:bg-blue-700"
                    >
                      {latestRoadmap ? "Continue" : "Generate"}
                    </button>
                  </div>
                </div>

                <div className="bg-white p-6 rounded-lg shadow">
                  <h2 className="text-lg mb-2 text-gray-800">Quiz Performance</h2>
                  <div className="flex flex-col items-center">
                    <div className="relative w-24 h-24">
                      <svg className="w-full h-full" viewBox="0 0 36 36">
                        <path
                          strokeWidth="3.8" fill="none" stroke="#e5e7eb"
                          d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                        />
                        <path
                          strokeWidth="3.8" fill="none" stroke="#2563eb"
                          strokeDasharray={`${avgScore}, 100`}
                          d="M18 2.0845 a 15.9155 15.9155 0 0 1 0 31.831 a 15.9155 15.9155 0 0 1 0 -31.831"
                        />
                      </svg>
                      <span className="absolute inset-0 flex items-center justify-center text-lg font-semibold text-blue-600">
                        {avgScore}%
                      </span>
                    </div>
                    <p className="text-sm text-gray-500 mt-2">
                      {quizResults.length} quiz{quizResults.length !== 1 ? "zes" : ""} taken
                    </p>
                  </div>
                </div>
              </div>

              {/* Stats row */}
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-10">
                <div className="bg-white p-6 rounded-lg shadow text-center">
                  <p className="text-sm text-gray-500 mb-1">Quizzes Taken</p>
                  <p className="text-3xl font-bold text-blue-600">{quizResults.length}</p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow text-center">
                  <p className="text-sm text-gray-500 mb-1">Avg Quiz Score</p>
                  <p className="text-3xl font-bold text-green-600">{avgScore}%</p>
                </div>
                <div className="bg-white p-6 rounded-lg shadow text-center">
                  <p className="text-sm text-gray-500 mb-1">Weak Areas</p>
                  <p className="text-3xl font-bold text-orange-500">{uniqueWeak.length}</p>
                </div>
              </div>

              {/* Weak topics */}
              {uniqueWeak.length > 0 && (
                <div className="bg-white p-6 rounded-lg shadow mb-10">
                  <h2 className="text-lg font-bold text-gray-800 mb-4">Topics to Revise</h2>
                  <div className="flex flex-wrap gap-2">
                    {uniqueWeak.map((topic, i) => (
                      <span
                        key={i}
                        className="bg-orange-100 text-orange-700 px-3 py-1 rounded-full text-sm font-medium"
                      >
                        {topic}
                      </span>
                    ))}
                  </div>
                </div>
              )}

              {/* Recent quiz results */}
              {quizResults.length > 0 && (
                <div className="bg-white p-6 rounded-lg shadow mb-10">
                  <h2 className="text-lg font-bold text-gray-800 mb-4">Recent Quiz Results</h2>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm text-left">
                      <thead>
                        <tr className="border-b text-gray-500">
                          <th className="pb-2 pr-4">Topic</th>
                          <th className="pb-2 pr-4">Score</th>
                          <th className="pb-2">Date</th>
                        </tr>
                      </thead>
                      <tbody>
                        {[...quizResults].reverse().slice(0, 5).map((r, i) => {
                          const pct = Math.round((r.score / r.total_questions) * 100);
                          return (
                            <tr key={i} className="border-b last:border-none">
                              <td className="py-2 pr-4 text-gray-800">{r.topic}</td>
                              <td className="py-2 pr-4">
                                <span className={`font-semibold ${pct >= 70 ? "text-green-600" : "text-red-500"}`}>
                                  {r.score}/{r.total_questions} ({pct}%)
                                </span>
                              </td>
                              <td className="py-2 text-gray-400 text-xs">
                                {r.timestamp ? new Date(r.timestamp).toLocaleDateString() : "—"}
                              </td>
                            </tr>
                          );
                        })}
                      </tbody>
                    </table>
                  </div>
                </div>
              )}

              {/* Empty state */}
              {quizResults.length === 0 && !latestRoadmap && (
                <div className="bg-white p-10 rounded-lg shadow text-center text-gray-500">
                  <p className="text-lg mb-4">No activity yet. Start your journey!</p>
                  <button
                    onClick={() => navigate("/roadmap")}
                    className="bg-blue-600 text-white px-6 py-2 rounded-md hover:bg-blue-700"
                  >
                    Generate a Roadmap
                  </button>
                </div>
              )}
            </>
          )}
        </main>
      </div>
      <Footer />
    </div>
  );
}
