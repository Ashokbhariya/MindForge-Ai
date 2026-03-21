const BASE_URL = "http://127.0.0.1:8000";

export const api = {
  // ---------------- AUTH ----------------
    signup: (data) =>
        fetch(`${BASE_URL}/auth/register`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
        }).then((res) => res.json()),

    login: async (data) => {
    try {
        const res = await fetch(`${BASE_URL}/auth/login`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(data),
        });

        if (!res.ok) {
        const error = await res.json();
        throw new Error(error.detail || "Login failed");
        }

        const result = await res.json();
        return { data: result };  // wrap in `.data` for frontend compatibility
    } catch (err) {
        console.error("Login error:", err);
        throw err;
    }
    },

    // ---------------- USERS ----------------
    getUser: (userId) =>
        fetch(`${BASE_URL}/users/${userId}`).then((res) => res.json()),

    // ---------------- ROADMAP ----------------
    generateRoadmap: (payload) => {
        const body = {
        prompt: payload?.prompt || payload?.text || "",
        user_id: payload?.user_id || "123e4567-e89b-12d3-a456-426614174000",
        level: payload?.level || "beginner",
        };

        return fetch(`${BASE_URL}/api/generate-roadmap`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
        }).then((res) => res.json());
    },

    getRoadmap: () =>
        fetch(`${BASE_URL}/api/get-roadmap`).then((res) => res.json()),

    searchRoadmap: (payload) =>
        fetch(`${BASE_URL}/api/search-roadmap`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(payload),
        }).then((res) => res.json()),

    // ---------------- QUIZ ----------------
    generateQuiz: ({ topic, user_id, count }) =>
        fetch(`${BASE_URL}/api/quiz/quiz/generate`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ topic, user_id, count }),
        }).then((res) => {
            if (!res.ok) {
                console.error("Failed to generate quiz", res.status);
            }
            return res.json();
        }),

    submitQuiz: (data) =>
        fetch(`${BASE_URL}/api/quiz/quiz/submit`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(data),
        }).then((res) => res.json()),

    getScore: (attemptId) =>
        fetch(`${BASE_URL}/api/quiz/quiz/score/${attemptId}`).then((res) =>
            res.json()
        ),

    // ---------------- CONFUSION SIGNALS ----------------
    createConfusionSignal: (data) =>
        fetch(`${BASE_URL}/confusion-signals/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
        }).then((res) => res.json()),

    getConfusionSignals: (userId) =>
        fetch(`${BASE_URL}/confusion-signals/${userId}`).then((res) =>
        res.json()
        ),

    getConfusionQuiz: (topic) =>
        fetch(`${BASE_URL}/confusion-signals/quiz/${topic}`).then((res) =>
        res.json()
        ),

    attemptConfusionQuiz: (data) =>
        fetch(`${BASE_URL}/confusion-signals/quiz/attempt`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
        }).then((res) => res.json()),

    // ---------------- RECALL CARDS ----------------
    getRecallCards: (userId) =>
        fetch(`${BASE_URL}/recall-cards/${userId}`).then((res) => res.json()),

    createRecallCard: (data) =>
        fetch(`${BASE_URL}/recall-cards/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
        }).then((res) => res.json()),

    createRecallCardAuto: ({ user_id, topic }) =>
        fetch(`${BASE_URL}/recall-cards/generate`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ user_id, topic }),
        }).then((res) => res.json()),

    // ---------------- LEARNING STYLE ----------------
    getLearningStyle: (userId) =>
        fetch(`${BASE_URL}/learning-style/learning-style/${userId}`).then((res) =>
        res.json()
        ),

    createLearningStyle: (data) =>
        fetch(`${BASE_URL}/learning-style/learning-style/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
        }).then((res) => res.json()),

    // ---------------- KNOWLEDGE DECAY ----------------
    getKnowledgeDecay: (userId) =>
        fetch(`${BASE_URL}/knowledge-decay/knowledge-decay/${userId}`).then(
        (res) => res.json()
        ),

    createKnowledgeDecay: (data) =>
        fetch(`${BASE_URL}/knowledge-decay/knowledge-decay/`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(data),
        }).then((res) => res.json()),

    // ---------------- YOUTUBE API ----------------
    fetchYouTubeLinks: (topic) =>
        fetch(`${BASE_URL}/api/youtube-links`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic }),
        })
        .then((response) => {
            if (!response.ok) {
            console.error("Failed to fetch YouTube links:", response.statusText);
            return { videos: [] };
            }
            return response.json();
        })
        .catch((error) => {
            console.error("Error fetching YouTube links:", error);
            return { videos: [] };
        }),

    // ---------------- PDF API ----------------
    generatePDF: (topic) =>
        fetch(`${BASE_URL}/api/generate-pdf`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ topic }),
        })
        .then((res) => {
            if (!res.ok) throw new Error("PDF generation failed");
            return res.json();
        })
        .catch((err) => {
            console.error("Error in generatePDF:", err);
            return { pdf_url: null };
        }),
};
