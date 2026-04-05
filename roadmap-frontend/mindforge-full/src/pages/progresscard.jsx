import React, { useEffect, useState } from "react";
import { Bar, Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  CategoryScale,
  LinearScale,
  BarElement,
  Title,
  Tooltip,
  Legend,
  ArcElement,
} from "chart.js";
import "../pages/ProgressCard.css";

ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

const BASE_URL = "http://127.0.0.1:8000";

// FIX: read userId directly from localStorage instead of relying on a prop
// (App.jsx renders <ProgressCardPage /> with no props, so the old userId prop was always undefined)
const getUserId = () => {
  try {
    const user = JSON.parse(localStorage.getItem("user") || "{}");
    return user.id || user.user_id || null;
  } catch {
    return null;
  }
};

export default function ProgressCard() {
  const [quizResults, setQuizResults] = useState([]);
  const [isLoading, setIsLoading]     = useState(true);
  const [error, setError]             = useState("");

  useEffect(() => {
    async function fetchData() {
      const userId = getUserId();
      if (!userId) {
        setError("Please log in to see your progress.");
        setIsLoading(false);
        return;
      }
      try {
        const res = await fetch(`${BASE_URL}/api/quiz/results?user_id=${userId}`);
        if (!res.ok) throw new Error("Failed to fetch quiz results");
        const data = await res.json();
        setQuizResults(Array.isArray(data) ? data : []);
        setError("");
      } catch {
        setError("Unable to load progress data right now.");
      } finally {
        setIsLoading(false);
      }
    }
    fetchData();
  }, []);

  const totalQuizzes = quizResults.length;

  const avgScore = totalQuizzes
    ? Math.round(
        quizResults.reduce((sum, r) => sum + (r.score / r.total_questions) * 100, 0) / totalQuizzes
      )
    : 0;

  const topicMap = {};
  quizResults.forEach((r) => {
    const pct = Math.round((r.score / r.total_questions) * 100);
    if (!topicMap[r.topic]) topicMap[r.topic] = [];
    topicMap[r.topic].push(pct);
  });
  const topicLabels = Object.keys(topicMap).slice(-6);
  const topicAvgs   = topicLabels.map((t) =>
    Math.round(topicMap[t].reduce((a, b) => a + b, 0) / topicMap[t].length)
  );

  const barData = {
    labels: topicLabels.length > 0 ? topicLabels : ["No data yet"],
    datasets: [{
      label: "Avg Score (%)",
      data: topicLabels.length > 0 ? topicAvgs : [0],
      backgroundColor: "#2196F3",
      borderRadius: 6,
    }],
  };

  const barOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: { display: false },
      title: { display: true, text: "Score by Topic" },
    },
    scales: { y: { beginAtZero: true, max: 100 } },
  };

  const passed = quizResults.filter(
    (r) => Math.round((r.score / r.total_questions) * 100) >= 70
  ).length;

  const pieData = {
    labels: ["Passed (≥70%)", "Needs Improvement"],
    datasets: [{
      data: [passed || 0, (totalQuizzes - passed) || 0],
      backgroundColor: ["#4CAF50", "#FFC107"],
    }],
  };

  const pieOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: { legend: { position: "bottom" } },
  };

  return (
    <div className="progress-card">
      <div className="pc-header">
        <h2>Your Progress Overview</h2>
        {avgScore >= 80 && <span className="pc-badge">Great job! 🎉</span>}
      </div>

      {isLoading && (
        <div className="pc-loading">
          <div className="pc-spinner" />
          <p>Loading your progress…</p>
        </div>
      )}

      {!isLoading && error && (
        <div className="pc-error"><p>{error}</p></div>
      )}

      {!isLoading && !error && totalQuizzes === 0 && (
        <div className="pc-error">
          <p>No quiz data yet. Take a quiz to see your progress here!</p>
        </div>
      )}

      {!isLoading && !error && totalQuizzes > 0 && (
        <>
          <div className="pc-stats">
            <div className="pc-stat">
              <span className="pc-stat-label">Quizzes Taken</span>
              <span className="pc-stat-value">{totalQuizzes}</span>
            </div>
            <div className="pc-stat">
              <span className="pc-stat-label">Avg Score</span>
              <span className="pc-stat-value">{avgScore}%</span>
            </div>
            <div className="pc-stat">
              <span className="pc-stat-label">Passed</span>
              <span className="pc-stat-value">{passed}/{totalQuizzes}</span>
            </div>
          </div>

          <div className="pc-grid">
            <div className="chart-box">
              <Bar data={barData} options={barOptions} />
            </div>
            <div className="chart-box">
              <Pie data={pieData} options={pieOptions} />
            </div>
          </div>
        </>
      )}
    </div>
  );
}