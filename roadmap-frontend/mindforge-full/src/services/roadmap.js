import React, { useEffect, useState } from "react";
import { api } from "./api";  // Tumhare api.js se functions le rahe hain

const BASE_URL = "http://127.0.0.1:8000";

const Roadmap = () => {
    const [roadmapData, setRoadmapData] = useState([]);
    const [quizData, setQuizData] = useState(null);
    const [loading, setLoading] = useState(false);

    // GET Roadmap (direct fetch)
    const getRoadmap = () =>
        fetch(`${BASE_URL}/api/get-roadmap`)
        .then((res) => {
            if (!res.ok) throw new Error("Failed to fetch roadmap");
            return res.json();
        });

    // Load roadmap on component mount
    useEffect(() => {
        getRoadmap()
        .then((data) => setRoadmapData(data))
        .catch((err) => console.error("Error fetching roadmap:", err));
    }, []);

    // Handle Generate Quiz
    const handleGenerateQuiz = async (topic) => {
        try {
        setLoading(true);
        setQuizData(null);
        const response = await api.generateQuiz(topic, 5); // Default 5 questions
        setQuizData(response.quiz || response);
        } catch (error) {
        console.error("Error generating quiz:", error);
        } finally {
        setLoading(false);
        }
    };

    return (
        <div>
        <h2 className="text-xl font-bold">Roadmap Infographic</h2>
        {console.log("Roadmap Component Loaded")}
        <div className="roadmap-container">
            {roadmapData.map((topic, index) => (
            <div key={index} className="roadmap-card">
                <h3 className="font-semibold">{topic.title}</h3>
                <p>{topic.description}</p>
                <a href={topic.resourceUrl} className="view-link">
                View Resource
                </a>

                {/* NEW Generate Quiz Button */}
                <button
                className="generate-quiz-btn"
                onClick={() => handleGenerateQuiz(topic.title)}
                >
                Generate Quiz
                </button>
            </div>
            ))}
        </div>

        {/* Show Quiz */}
        {loading && <p>Generating quiz...</p>}
        {quizData && (
            <div className="quiz-section mt-4 p-4 border rounded">
            <h3 className="font-bold text-lg">Quiz</h3>
            <pre className="bg-gray-100 p-2 rounded">{quizData}</pre>
            </div>
        )}
        </div>
    );
};

export default Roadmap;
