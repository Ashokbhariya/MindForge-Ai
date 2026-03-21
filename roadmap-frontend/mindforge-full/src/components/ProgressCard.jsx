import React, { useEffect, useState } from "react";
import axios from "axios";
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
    import "./ProgressCard.css";

    ChartJS.register(
    CategoryScale,
    LinearScale,
    BarElement,
    Title,
    Tooltip,
    Legend,
    ArcElement
    );

    export default function ProgressCard({ userId }) {
    const [progress, setProgress] = useState(0);
    const [avgQuiz, setAvgQuiz] = useState(0);
    const [sessions, setSessions] = useState(0);
    const [isLoading, setIsLoading] = useState(true);
    const [error, setError] = useState("");

    const storageKey = `progress_summary_${userId}`;

    // ✅ Load cached progress from localStorage (instant feedback)
    useEffect(() => {
        const savedData = localStorage.getItem(storageKey);
        if (savedData) {
        try {
            const { completion_percent, avg_quiz_score, total_sessions } =
            JSON.parse(savedData);
            setProgress(Math.round(completion_percent || 0));
            setAvgQuiz(Math.round(avg_quiz_score || 0));
            setSessions(total_sessions || 0);
            setIsLoading(false);
        } catch {
            console.warn("Invalid cached progress data");
        }
        }
    }, [userId, storageKey]);

    // ✅ Fetch fresh data from backend
    useEffect(() => {
        let active = true;
        async function fetchProgress() {
        try {
            const res = await axios.get(`/progress-card/${userId}/summary`);
            if (!active) return;
            const { completion_percent, avg_quiz_score, total_sessions } =
            res.data || {};
            setProgress(Math.round(completion_percent || 0));
            setAvgQuiz(Math.round(avg_quiz_score || 0));
            setSessions(total_sessions || 0);

            localStorage.setItem(storageKey, JSON.stringify(res.data || {}));
            setError("");
        } catch (err) {
            setError("Unable to load progress data right now.");
        } finally {
            if (active) setIsLoading(false);
        }
        }
        fetchProgress();
        return () => {
        active = false;
        };
    }, [userId, storageKey]);

    // 📊 Bar chart config
    const barData = {
        labels: ["Sessions", "Avg Quiz Score (%)"],
        datasets: [
        {
            label: "Stats",
            data: [sessions, avgQuiz],
            backgroundColor: ["#2196F3", "#4CAF50"],
            borderRadius: 6,
        },
        ],
    };

    const barOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
        legend: { display: false },
        title: { display: true, text: "Learning Stats" },
        tooltip: {
            callbacks: {
            label: (ctx) => `${ctx.dataset.label}: ${ctx.parsed.y}`,
            },
        },
        },
        scales: { y: { beginAtZero: true } },
    };

    // 🍰 Pie chart config
    const pieData = {
        labels: ["Completed (%)", "Remaining (%)"],
        datasets: [
        {
            data: [progress, Math.max(0, 100 - progress)],
            backgroundColor: ["#4CAF50", "#FFC107"],
        },
        ],
    };

    const pieOptions = {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
        legend: { position: "bottom" },
        tooltip: {
            callbacks: {
            label: (ctx) => `${ctx.label}: ${Math.round(ctx.parsed || 0)}%`,
            },
        },
        },
    };

    return (
        <div className="progress-card">
        <div className="pc-header">
            <h2>Your Progress Overview</h2>
            {progress >= 80 && <span className="pc-badge">Great job! 🎉</span>}
        </div>

        {/* Loading state */}
        {isLoading && (
            <div className="pc-loading">
            <div className="pc-spinner" />
            <p>Loading your progress…</p>
            </div>
        )}

        {/* Error state */}
        {!isLoading && error && (
            <div className="pc-error">
            <p>{error}</p>
            <small>Showing last saved snapshot (if available).</small>
            </div>
        )}

        {/* Stats */}
        {!isLoading && (
            <>
            <div className="pc-stats">
                <div className="pc-stat">
                <span className="pc-stat-label">Total Sessions</span>
                <span className="pc-stat-value">{sessions}</span>
                </div>
                <div className="pc-stat">
                <span className="pc-stat-label">Overall Progress</span>
                <span className="pc-stat-value">{progress}%</span>
                </div>
                <div className="pc-stat">
                <span className="pc-stat-label">Avg Quiz Score</span>
                <span className="pc-stat-value">{avgQuiz}%</span>
                </div>
            </div>

            {/* Charts */}
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
