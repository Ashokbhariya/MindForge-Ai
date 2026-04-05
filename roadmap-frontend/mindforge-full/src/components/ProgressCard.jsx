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

    ChartJS.register(CategoryScale, LinearScale, BarElement, Title, Tooltip, Legend, ArcElement);

    const BASE_URL = "http://127.0.0.1:8000";

    // FIX: Single unified component — no more double default export
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
        // FIX: Check for userId directly — no need for separate page wrapper
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
        } catch (err) {
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
            quizResults.reduce((sum, r) => sum + (r.score / r.total_questions) * 100, 0) /
            totalQuizzes
        )
        : 0;

    const topicMap = {};
    quizResults.forEach((r) => {
        const pct = Math.round((r.score / r.total_questions) * 100);
        if (!topicMap[r.topic]) topicMap[r.topic] = [];
        topicMap[r.topic].push(pct);
    });
    const topicLabels = Object.keys(topicMap).slice(-6);
    const topicAvgs   = topicLabels.map((t) => {
        const scores = topicMap[t];
        return Math.round(scores.reduce((a, b) => a + b, 0) / scores.length);
    });

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
    const failed = totalQuizzes - passed;

    const pieData = {
        labels: ["Passed (≥70%)", "Needs Improvement"],
        datasets: [{
        data: [passed || 0, failed || 0],
        backgroundColor: ["#4CAF50", "#FFC107"],
        }],
    };

    const pieOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: { legend: { position: "bottom" } },
    };

    return (
        <div style={{ padding: "24px", fontFamily: "Inter, sans-serif" }}>
        <div style={{ display: "flex", alignItems: "center", justifyContent: "space-between", marginBottom: "16px" }}>
            <h2 style={{ fontSize: "22px", fontWeight: "700", color: "#1a213d" }}>Your Progress Overview</h2>
            {avgScore >= 80 && (
            <span style={{ background: "#d1fae5", color: "#065f46", padding: "4px 12px", borderRadius: "999px", fontSize: "13px", fontWeight: "600" }}>
                Great job! 🎉
            </span>
            )}
        </div>

        {isLoading && (
            <div style={{ display: "flex", alignItems: "center", gap: "12px", padding: "24px" }}>
            <div style={{ width: "28px", height: "28px", borderRadius: "50%", border: "3px solid #2563eb", borderTopColor: "transparent", animation: "spin 0.8s linear infinite" }} />
            <p style={{ color: "#6b7280" }}>Loading your progress…</p>
            </div>
        )}

        {!isLoading && error && (
            <div style={{ background: "#f3f4f6", border: "1px solid #e5e7eb", borderRadius: "8px", padding: "16px 20px", color: "#6b7280" }}>
            <p>{error}</p>
            </div>
        )}

        {!isLoading && !error && totalQuizzes === 0 && (
            <div style={{ background: "#f3f4f6", border: "1px solid #e5e7eb", borderRadius: "8px", padding: "16px 20px", color: "#6b7280" }}>
            <p>No quiz data yet. Take a quiz to see your progress here!</p>
            </div>
        )}

        {!isLoading && !error && totalQuizzes > 0 && (
            <>
            {/* Stats row */}
            <div style={{ display: "grid", gridTemplateColumns: "repeat(3, 1fr)", gap: "16px", marginBottom: "24px" }}>
                {[
                { label: "Quizzes Taken", value: totalQuizzes, color: "#2563eb" },
                { label: "Avg Score",     value: `${avgScore}%`, color: "#16a34a" },
                { label: "Passed",        value: `${passed}/${totalQuizzes}`, color: "#9333ea" },
                ].map((s) => (
                <div key={s.label} style={{ background: "#fff", border: "1px solid #e5e7eb", borderRadius: "10px", padding: "18px", textAlign: "center", boxShadow: "0 1px 3px rgba(0,0,0,0.06)" }}>
                    <p style={{ color: "#6b7280", fontSize: "13px", marginBottom: "6px" }}>{s.label}</p>
                    <p style={{ color: s.color, fontSize: "28px", fontWeight: "700" }}>{s.value}</p>
                </div>
                ))}
            </div>

            {/* Charts */}
            <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "20px" }}>
                <div style={{ background: "#fff", border: "1px solid #e5e7eb", borderRadius: "10px", padding: "16px", height: "260px", boxShadow: "0 1px 3px rgba(0,0,0,0.06)" }}>
                <Bar data={barData} options={barOptions} />
                </div>
                <div style={{ background: "#fff", border: "1px solid #e5e7eb", borderRadius: "10px", padding: "16px", height: "260px", boxShadow: "0 1px 3px rgba(0,0,0,0.06)" }}>
                <Pie data={pieData} options={pieOptions} />
                </div>
            </div>

            {/* Recent results table */}
            <div style={{ background: "#fff", border: "1px solid #e5e7eb", borderRadius: "10px", padding: "20px", marginTop: "20px", boxShadow: "0 1px 3px rgba(0,0,0,0.06)" }}>
                <h3 style={{ fontSize: "15px", fontWeight: "600", color: "#1f2937", marginBottom: "12px" }}>Recent Quiz Results</h3>
                <table style={{ width: "100%", fontSize: "13px", borderCollapse: "collapse" }}>
                <thead>
                    <tr style={{ borderBottom: "1px solid #e5e7eb", color: "#6b7280" }}>
                    <th style={{ textAlign: "left", paddingBottom: "8px" }}>Topic</th>
                    <th style={{ textAlign: "left", paddingBottom: "8px" }}>Score</th>
                    <th style={{ textAlign: "left", paddingBottom: "8px" }}>Date</th>
                    </tr>
                </thead>
                <tbody>
                    {[...quizResults].reverse().slice(0, 6).map((r, i) => {
                    const pct = Math.round((r.score / r.total_questions) * 100);
                    return (
                        <tr key={i} style={{ borderBottom: "1px solid #f3f4f6" }}>
                        <td style={{ padding: "8px 0", color: "#374151" }}>{r.topic}</td>
                        <td style={{ padding: "8px 0", fontWeight: "600", color: pct >= 70 ? "#16a34a" : "#dc2626" }}>
                            {r.score}/{r.total_questions} ({pct}%)
                        </td>
                        <td style={{ padding: "8px 0", color: "#9ca3af" }}>
                            {r.timestamp ? new Date(r.timestamp).toLocaleDateString() : "—"}
                        </td>
                        </tr>
                    );
                    })}
                </tbody>
                </table>
            </div>
            </>
        )}
        </div>
    );
    }