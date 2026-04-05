import React, { useState, useEffect, useRef } from 'react';
import { motion } from 'framer-motion';
import { useLocation } from 'react-router-dom';
import Navbar from '../components/DashNav';
import Footer from '../components/Footer';
import { api } from '../services/api';
import RoadmapInfographic from '../components/RoadmapInfographic';

export default function Roadmap() {
  const location = useLocation();

  const [topic, setTopic]     = useState('');
  const [level, setLevel]     = useState('Beginner');
  const [roadmap, setRoadmap] = useState(null);
  const [loading, setLoading] = useState(false);

  // Use a ref so autoGenerate can read the latest topic without stale closure
  const topicRef = useRef('');
  const levelRef = useRef('Beginner');

  useEffect(() => {
    topicRef.current = topic;
  }, [topic]);

  useEffect(() => {
    levelRef.current = level;
  }, [level]);

  // ── Pre-fill + auto-generate when coming from Dashboard ───────
  useEffect(() => {
    if (!location.state) return;

    const { prefill, level: stateLevel, autoGenerate } = location.state;

    let resolvedTopic = '';
    let resolvedLevel = 'Beginner';

    if (prefill) {
      resolvedTopic = prefill;
      setTopic(prefill);
      topicRef.current = prefill;
    }

    if (stateLevel) {
      const l = stateLevel.charAt(0).toUpperCase() + stateLevel.slice(1).toLowerCase();
      resolvedLevel = l;
      setLevel(l);
      levelRef.current = l;
    }

    if (autoGenerate && resolvedTopic) {
      // Small delay to let React render the state, then generate
      setTimeout(() => {
        triggerGenerate(resolvedTopic, resolvedLevel);
      }, 150);
    }
  }, [location.state]);

  // ── Separate generate function that takes args directly ────────
  const triggerGenerate = async (topicArg, levelArg) => {
    if (!topicArg?.trim()) return;
    setLoading(true);

    let userId = "00000000-0000-0000-0000-000000000001";
    try {
      const stored = localStorage.getItem("user");
      if (stored) userId = JSON.parse(stored)?.id || userId;
    } catch { /* ignore */ }

    try {
      const data = await api.generateRoadmap({
        prompt: topicArg,
        user_id: userId,
        level: levelArg.toLowerCase(),
      });
      if (data?.data) {
        setRoadmap(data.data);
      } else {
        alert('No roadmap data received from server.');
      }
    } catch (error) {
      console.error('Error generating roadmap:', error);
      alert('Failed to generate roadmap. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  // ── Manual generate button handler ────────────────────────────
  const handleGenerateRoadmap = () => triggerGenerate(topic, level);

  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary to-white flex flex-col text-dark">
      <Navbar />

      <main className="flex-1 flex flex-col items-center justify-start px-4 py-12">
        <motion.h1
          className="text-4xl font-bold text-primary mb-4 text-center"
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
        >
          Roadmap
        </motion.h1>
        <p className="text-lg text-gray-700 max-w-2xl text-center mb-8">
          Enter your career goal or a topic you'd like to master — MindForgeAI will
          generate a personalised learning path.
        </p>

        {/* Input section */}
        <div className="w-full max-w-md mb-10 space-y-4">
          <input
            type="text"
            value={topic}
            onChange={(e) => setTopic(e.target.value)}
            placeholder="e.g., Data Structures, Cybersecurity"
            className="w-full px-4 py-3 rounded-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary"
          />

          <select
            value={level}
            onChange={(e) => setLevel(e.target.value)}
            className="w-full px-4 py-3 rounded-md border border-gray-300 focus:outline-none focus:ring-2 focus:ring-primary"
          >
            <option value="Beginner">Beginner</option>
            <option value="Intermediate">Intermediate</option>
            <option value="Advanced">Advanced</option>
          </select>

          <button
            onClick={handleGenerateRoadmap}
            className="w-full bg-primary text-white font-semibold py-3 rounded-md shadow hover:bg-[#0f3c8c] transition"
            disabled={loading}
          >
            {loading ? "Generating…" : "Generate Roadmap"}
          </button>
        </div>

        {/* Loading indicator */}
        {loading && (
          <div className="flex items-center justify-center mb-8">
            <div className="animate-spin rounded-full h-10 w-10 border-b-2 border-primary" />
            <span className="ml-3 text-gray-500">Generating your roadmap…</span>
          </div>
        )}

        {/* Roadmap output */}
        {roadmap && (
          <div className="w-full max-w-7xl bg-white p-10 rounded-xl shadow-lg text-left">
            <h3 className="text-xl font-semibold text-primary mb-2">
              Personalised Roadmap ({level}):
            </h3>
            <RoadmapInfographic roadmap={roadmap} />
          </div>
        )}
      </main>

      <Footer />
    </div>
  );
}