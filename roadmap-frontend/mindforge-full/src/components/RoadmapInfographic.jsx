    import React from "react";
    import { motion } from "framer-motion";
    import { useNavigate } from "react-router-dom";

    const colors = ["#e74c3c", "#f39c12", "#27ae60", "#2980b9", "#8e44ad"];

    // Generates a direct GFG topic URL from the title
    const getGFGLink = (title) => {
    const slug = title
        .trim()
        .toLowerCase()
        .replace(/[^a-z0-9\s-]/g, "") // remove special chars
        .replace(/\s+/g, "-") // spaces → hyphens
        .replace(/-+/g, "-"); // collapse multiple hyphens

    return `https://www.geeksforgeeks.org/${slug}/`;
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
            <div className="h-full w-2 border-dashed border-white border-l-2 ml-5"></div>
            </div>

            {/* Subtopic Cards */}
            {roadmap.subtopics.map((s, index) => {
            const isEven = index % 2 === 0;
            const cardWidth = 300;
            const dotSize = 14;
            const verticalSpacing = 200;
            const gapFromCenter = 32;

            const gfgLink = s.link || getGFGLink(s.title);

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
                        backgroundColor: colors[index % colors.length] + "22",
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

                    {/* GFG Link */}
                    <div className="mt-3">
                        <a
                        href={gfgLink}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="flex items-center justify-center gap-1 px-3 py-1.5 bg-green-50 text-green-700 text-xs rounded-lg hover:bg-green-100 transition font-medium w-full border border-green-200"
                        >
                        📖 Read on GFG
                        </a>
                    </div>

                    {/* Quiz button */}
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