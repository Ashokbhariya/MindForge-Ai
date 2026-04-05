import React, { useState } from "react";
import { motion } from "framer-motion";
import { useNavigate } from "react-router-dom";

import Navbar from "../components/DashNav.jsx";
import Footer from "../components/Footer.jsx";
import { api } from "../services/api.js";

export default function LearnQuiz() {
  const [inputValue, setInputValue] = useState("");
  const [selectedFormat, setSelectedFormat] = useState("pdf");

  const [pdfUrl, setPdfUrl] = useState("");
  const [videoLinks, setVideoLinks] = useState([]);

  const [loadingContent, setLoadingContent] = useState(false);
  const [loadingQuiz, setLoadingQuiz] = useState(false);

  const navigate = useNavigate();

  const resetPreviews = () => {
    setPdfUrl("");
    setVideoLinks([]);
  };

  const handleGenerateContent = async () => {
    const topic = inputValue.trim();

    if (!topic) {
      alert("Please enter a topic first.");
      return;
    }

    resetPreviews();
    setLoadingContent(true);

    try {
      if (selectedFormat === "pdf") {
        const res = await api.generatePDF(topic);

        if (res?.pdf_url) {
          setPdfUrl(res.pdf_url);
        } else {
          alert("Failed to generate PDF.");
        }
      } else if (selectedFormat === "video") {
        const res = await api.fetchYouTubeLinks(topic);
        const links = Array.isArray(res?.videos) ? res.videos : [];

        if (links.length > 0) {
          setVideoLinks(links);
        } else {
          alert("No videos found for this topic.");
        }
      } else {
        alert("Invalid format selected.");
      }
    } catch (error) {
      console.error("Content generation error:", error);
      alert("Something went wrong while generating content.");
    } finally {
      setLoadingContent(false);
    }
  };

  const handleGenerateQuiz = async () => {
    const topic = inputValue.trim();

    if (!topic) {
      alert("Please enter a topic first.");
      return;
    }

    try {
      setLoadingQuiz(true);
      navigate(`/quiz/${encodeURIComponent(topic)}`);
    } catch (error) {
      console.error("Quiz navigation error:", error);
      alert("Unable to open quiz.");
    } finally {
      setLoadingQuiz(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary to-white text-dark flex flex-col">
      <Navbar />

      <motion.section
        className="flex-1 flex flex-col items-center justify-center text-center px-6 py-20"
        initial={{ opacity: 0, y: 40 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
      >
        <h1 className="text-4xl md:text-5xl font-bold text-primary mb-4">
          Learn & Quiz
        </h1>

        <p className="text-lg text-gray-700 max-w-2xl mb-8">
          Enter a topic, generate learning content in your preferred format,
          and test your understanding with a quiz.
        </p>

        <div className="w-full max-w-2xl bg-white p-6 md:p-8 rounded-2xl shadow-lg text-left">
          <h3 className="text-2xl font-semibold text-primary mb-4">
            Today’s Topic
          </h3>

          <input
            type="text"
            placeholder="e.g. Machine Learning, SQL Joins, React Hooks"
            value={inputValue}
            onChange={(e) => setInputValue(e.target.value)}
            className="w-full py-3 px-4 border border-gray-300 rounded-2xl shadow-sm focus:outline-none focus:ring-2 focus:ring-primary"
          />

          <div className="mt-5">
            <label className="block mb-2 text-sm font-medium text-gray-700">
              Select Content Format
            </label>
            <select
              value={selectedFormat}
              onChange={(e) => setSelectedFormat(e.target.value)}
              className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary"
            >
              <option value="pdf">PDF</option>
              <option value="video">Video</option>
            </select>
          </div>

          <div className="flex flex-wrap gap-3 mt-6">
            <button
              onClick={handleGenerateContent}
              disabled={loadingContent}
              className="bg-primary text-white px-6 py-3 rounded-xl hover:bg-blue-700 transition-all disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {loadingContent ? "Generating..." : "Generate Content"}
            </button>

            <button
              onClick={handleGenerateQuiz}
              disabled={loadingQuiz}
              className="bg-secondary text-white px-6 py-3 rounded-xl hover:bg-green-700 transition-all disabled:opacity-60 disabled:cursor-not-allowed"
            >
              {loadingQuiz ? "Opening Quiz..." : "Take Quiz"}
            </button>
          </div>

          {/* PDF Preview */}
          {pdfUrl && selectedFormat === "pdf" && (
            <div className="mt-8">
              <h4 className="text-sm font-semibold mb-3 text-gray-700">
                PDF Preview
              </h4>

              <iframe
                src={pdfUrl}
                title="PDF Preview"
                className="w-full h-96 border rounded-xl"
              />

              <div className="mt-4">
                <a
                  href={pdfUrl}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="inline-block bg-primary text-white px-5 py-2.5 rounded-xl hover:bg-blue-700 transition"
                >
                  View Fullscreen
                </a>
              </div>
            </div>
          )}

          {/* Video Preview */}
          {videoLinks.length > 0 && selectedFormat === "video" && (
            <div className="mt-8">
              <h4 className="text-sm font-semibold mb-3 text-gray-700">
                Top Videos
              </h4>

              <ul className="space-y-3">
                {videoLinks.map((link, index) => (
                  <li key={index}>
                    <a
                      href={link}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 hover:underline break-all"
                    >
                      {link}
                    </a>
                  </li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </motion.section>

      <Footer />
    </div>
  );
}