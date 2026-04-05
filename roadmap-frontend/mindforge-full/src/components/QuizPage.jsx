    import React, { useEffect, useState, useRef } from "react";
    import { useParams, useNavigate } from "react-router-dom";
    import { api } from "../services/api";

    const BASE_URL = "http://127.0.0.1:8000";

    const getUserId = () => {
    try {
        const user = JSON.parse(localStorage.getItem("user") || "{}");
        return user.id || user.user_id || null;
    } catch {
        return null;
    }
    };

    export default function QuizPage() {
    const { topic } = useParams();
    const navigate  = useNavigate();

    const [quizData, setQuizData]               = useState([]);
    const [loading, setLoading]                 = useState(true);
    const [selectedAnswers, setSelectedAnswers] = useState({});
    const [showAnswers, setShowAnswers]         = useState(false);
    const [scoreData, setScoreData]             = useState(null);
    const [submitted, setSubmitted]             = useState(false);
    const hasFetched = useRef(false);

    useEffect(() => {
        if (hasFetched.current) return;
        hasFetched.current = true;
        const fetchQuiz = async () => {
        try {
            const response = await api.generateQuiz({ topic, count: 10 });
            setQuizData(response.questions || []);
        } catch (error) {
            console.error("Error fetching quiz:", error);
        } finally {
            setLoading(false);
        }
        };
        fetchQuiz();
    }, [topic]);

    const handleOptionSelect = (idx, option) => {
        if (showAnswers) return;
        setSelectedAnswers((prev) => ({ ...prev, [idx]: option }));
    };

    const handleSubmit = async () => {
        if (submitted) return;
        setSubmitted(true);

        try {
        const userId = getUserId();

        const formattedAnswers = quizData.map((q, idx) => ({
            question_id: q.id,
            selected_answer: selectedAnswers[idx] || null,
        }));

        // Step 1: submit with user_id in body so the attempt record stores it
        const submitRes = await api.submitQuiz({
            topic,
            answers: formattedAnswers,
            user_id: userId,
        });

        const attemptId = submitRes.attempt_id;

        // Step 2: get score — correct URL is /api/score/{id} NOT /api/quiz/score/{id}
        const scoreUrl = userId
            ? `${BASE_URL}/api/score/${attemptId}?user_id=${userId}`
            : `${BASE_URL}/api/score/${attemptId}`;

        const scoreRes = await fetch(scoreUrl).then((r) => r.json());

        setScoreData(scoreRes);
        setShowAnswers(true);

        // Step 3: redirect to confusion detector if score < 75%
        const pct = scoreRes?.percentage ?? 0;
        if (pct < 75) {
            navigate("/confusion-detector", {
            state: {
                weakTopics: scoreRes?.weak_topics || [],
                score: scoreRes?.score ?? 0,
                total: scoreRes?.total ?? 0,
                percentage: pct,
            },
            });
        }
        } catch (error) {
        console.error("Quiz submission failed:", error);
        setSubmitted(false);
        }
    };

    if (loading) return <p className="p-4 text-center">Loading quiz...</p>;

    return (
        <div className="p-6 bg-gray-100 min-h-screen">
        <button onClick={() => navigate(-1)} className="mb-4 px-4 py-2 bg-gray-500 text-white rounded hover:bg-gray-700">
            ← Back
        </button>
        <h2 className="text-2xl font-bold mb-4">Quiz: "{topic}"</h2>

        {quizData.length === 0 && <p className="text-red-500">No questions found for this topic.</p>}

        {quizData.map((q, idx) => (
            <div key={q.id || idx} className="mb-4 p-3 border rounded bg-white shadow">
            <p className="font-medium">{idx + 1}. {q.question}</p>
            {(q.options || []).map((opt, i) => {
                const isCorrect  = showAnswers && opt === q.answer;
                const isSelected = selectedAnswers[idx] === opt;
                const isWrong    = showAnswers && isSelected && !isCorrect;
                return (
                <label key={i} className={`block mb-1 p-2 rounded cursor-pointer ${
                    isCorrect ? "bg-green-200" : isWrong ? "bg-red-200" : isSelected ? "bg-blue-100" : "hover:bg-gray-50"
                }`}>
                    <input type="radio" name={`q-${idx}`} value={opt} className="mr-2"
                    onChange={() => handleOptionSelect(idx, opt)}
                    checked={isSelected} disabled={showAnswers} />
                    {opt}
                </label>
                );
            })}
            </div>
        ))}

        {!showAnswers && quizData.length > 0 && (
            <button onClick={handleSubmit} disabled={submitted}
            className="mt-4 px-6 py-2 bg-blue-500 text-white rounded hover:bg-blue-700 disabled:opacity-50">
            {submitted ? "Submitting..." : "Submit & View Score"}
            </button>
        )}

        {scoreData && (
            <div className="mt-6 p-4 bg-purple-50 rounded border border-purple-200">
            <p className="text-lg font-bold text-purple-700">
                Score: {scoreData.score ?? 0} / {scoreData.total ?? 0} ({Math.round(scoreData.percentage ?? 0)}%)
            </p>
            {(scoreData.weak_topics || []).length > 0 && (
                <p className="text-sm text-gray-600 mt-1">
                Weak areas: {scoreData.weak_topics.join(", ")}
                </p>
            )}
            </div>
        )}
        </div>
    );
    }