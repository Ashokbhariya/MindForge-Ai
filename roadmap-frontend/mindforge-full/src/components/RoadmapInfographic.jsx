    import React from "react";
    import { motion } from "framer-motion";
    import { useNavigate } from "react-router-dom";

    const colors = ["#e74c3c", "#f39c12", "#27ae60", "#2980b9", "#8e44ad"];

    const TECH_KEYWORDS = [
    "python", "java", "javascript", "c++", "sql", "html", "css",
    "array", "linked list", "stack", "queue", "tree", "graph", "sorting",
    "dynamic programming", "recursion", "hashing", "binary", "algorithm",
    "data structure", "machine learning", "deep learning", "neural",
    "database", "dbms", "operating system", "network", "system design",
    "react", "node", "docker", "git", "cloud", "api", "oops"
    ];

    const isTechnical = (title) =>
    TECH_KEYWORDS.some((kw) => title.toLowerCase().includes(kw));

    // Returns best resource link — GFG for tech, Wikipedia for non-tech
    const getResourceLink = (title) => {
    if (isTechnical(title)) {
        return {
        url: `https://www.geeksforgeeks.org/search/?q=${encodeURIComponent(title)}`,
        label: "📖 Read on GFG",
        className:
            "bg-green-50 text-green-700 border-green-200 hover:bg-green-100",
        };
    }

    return {
        url: `https://en.wikipedia.org/wiki/Special:Search?search=${encodeURIComponent(title)}`,
        label: "🌐 Read on Wikipedia",
        className:
        "bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100",
    };
    };

    export default function RoadmapInfographic({ roadmap }) {
    const navigate = useNavigate();

    if (!roadmap || !roadmap.subtopics) return null;

    const handleGenerateQuiz = (topic) => {
        navigate(`/quiz/${encodeURIComponent(topic)}`);
    };

    return (
        <div className="relative w-full overflow-y-auto h-[700px]">
        <div
            className="relative w-full bg-gradient-to-b from-gray-200 to-gray-100 rounded-lg"
            style={{ height: `${roadmap.subtopics.length * 200 + 100}px` }}
        >
            {/* Vertical Line */}
            <div className="absolute left-1/2 top-0 h-full w-12 bg-gray-700 rounded-full transform -translate-x-1/2">
            <div className="h-full w-2 border-dashed border-white border-l-2 ml-5" />
            </div>

            {/* Subtopic Cards */}
            {roadmap.subtopics.map((s, index) => {
            const isEven = index % 2 === 0;
            const cardWidth = 300;
            const dotSize = 14;
            const verticalSpacing = 200;
            const gapFromCenter = 32;

            // Use backend link if present, else auto-detect
            const resource = s.link
                ? {
                    url: s.link,
                    label: s.link.includes("geeksforgeeks")
                    ? "📖 Read on GFG"
                    : "🌐 Read on Wikipedia",
                    className: s.link.includes("geeksforgeeks")
                    ? "bg-green-50 text-green-700 border-green-200 hover:bg-green-100"
                    : "bg-blue-50 text-blue-700 border-blue-200 hover:bg-blue-100",
                }
                : getResourceLink(s.title);

            return (
                <motion.div
                key={index}
                initial={{ opacity: 0, x: isEven ? -30 : 30 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.08 }}
                className="absolute w-full"
                style={{ top: `${index * verticalSpacing + 40}px` }}
                >
                <div className="relative flex items-center justify-center w-full">
                    {/* Dot */}
                    <div
                    className="absolute z-10"
                    style={{
                        width: `${dotSize}px`,
                        height: `${dotSize}px`,
                        backgroundColor: colors[index % colors.length],
                        borderRadius: "9999px",
                        top: 0,
                        left: `calc(50% - ${dotSize / 2}px)`,
                    }}
                    />

                    {/* Card */}
                    <div
                    className="p-4 bg-white rounded-xl shadow-md text-center border border-gray-100"
                    style={{
                        width: `${cardWidth}px`,
                        position: "absolute",
                        top: "-20px",
                        left: isEven
                        ? `calc(50% - ${gapFromCenter + cardWidth}px)`
                        : `calc(50% + ${gapFromCenter}px)`,
                    }}
                    >
                    {/* Step badge */}
                    <span
                        className="inline-block text-xs font-bold px-2 py-0.5 rounded-full mb-1"
                        style={{
                        backgroundColor:
                            colors[index % colors.length] + "22",
                        color: colors[index % colors.length],
                        }}
                    >
                        Step {index + 1}
                    </span>

                    <h3 className="text-sm font-bold text-gray-800 mt-1">
                        {s.title}
                    </h3>

                    <p className="text-xs text-gray-500 mt-1 leading-relaxed">
                        {s.description?.slice(0, 90) || ""}
                        {s.description?.length > 90 ? "…" : ""}
                    </p>

                    {/* Smart Resource Link */}
                    <div className="mt-3">
                        <a
                        href={resource.url}
                        target="_blank"
                        rel="noopener noreferrer"
                        className={`flex items-center justify-center gap-1 px-3 py-1.5 text-xs rounded-lg transition font-medium w-full border ${resource.className}`}
                        >
                        {resource.label}
                        </a>
                    </div>

                    {/* Quiz Button */}
                    <div className="mt-2">
                        <button
                        className="px-3 py-1.5 bg-blue-500 text-white text-xs rounded-lg hover:bg-blue-700 transition font-medium w-full"
                        onClick={() => handleGenerateQuiz(s.title)}
                        >
                        Generate Quiz
                        </button>
                    </div>
                    </div>
                </div>
                </motion.div>
            );
            })}
        </div>
        </div>
    );
    }