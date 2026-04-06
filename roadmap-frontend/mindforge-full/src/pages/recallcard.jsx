import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import axios from "axios";
import Navbar from "../components/DashNav";
import Footer from "../components/Footer";

const BASE_URL = "https://mindforge-backend-gwj4.onrender.com";

// ─── Rich Flip Card ───────────────────────────────────────────────────────────
function FlipCard({ frontTitle, frontSubtitle, backDefinition, backPoints, backAnalogy }) {
  const [flipped, setFlipped] = useState(false);
  return (
    <div
      className="relative w-full cursor-pointer"
      style={{ perspective: "1200px", minHeight: "340px" }}
      onClick={() => setFlipped((f) => !f)}
    >
      <div
        className="w-full h-full relative"
        style={{
          transformStyle: "preserve-3d",
          transition: "transform 0.6s cubic-bezier(.4,0,.2,1)",
          transform: flipped ? "rotateY(180deg)" : "rotateY(0deg)",
          minHeight: "340px",
        }}
      >
        {/* FRONT */}
        <div
          className="absolute inset-0 flex flex-col items-center justify-center rounded-2xl shadow-md px-8 py-8 gap-4"
          style={{ backfaceVisibility: "hidden", background: "#F0F4FF", minHeight: "340px" }}
        >
          <span className="text-xs font-semibold text-indigo-400 uppercase tracking-widest">Click to reveal answer</span>
          <h2 className="text-3xl font-extrabold text-[#1025f9] text-center leading-tight">{frontTitle}</h2>
          {frontSubtitle && <p className="text-sm text-gray-500 text-center max-w-sm italic">"{frontSubtitle}"</p>}
          <div className="mt-2 flex items-center gap-2 text-indigo-300">
            <span className="text-2xl">🃏</span>
            <span className="text-xs">Flip to learn</span>
          </div>
        </div>

        {/* BACK */}
        <div
          className="absolute inset-0 flex flex-col justify-start rounded-2xl shadow-md px-8 py-6 gap-4 overflow-auto"
          style={{
            backfaceVisibility: "hidden",
            transform: "rotateY(180deg)",
            background: "linear-gradient(135deg, #1025f9 0%, #6366f1 100%)",
            minHeight: "340px",
          }}
        >
          {backDefinition && (
            <div>
              <p className="text-xs font-bold text-indigo-200 uppercase tracking-widest mb-1">Definition</p>
              <p className="text-white text-sm leading-relaxed">{backDefinition}</p>
            </div>
          )}
          {backPoints?.length > 0 && (
            <div>
              <p className="text-xs font-bold text-indigo-200 uppercase tracking-widest mb-2">Key Facts</p>
              <ul className="space-y-1">
                {backPoints.map((pt, i) => (
                  <li key={i} className="flex items-start gap-2 text-white text-sm">
                    <span className="mt-1 w-1.5 h-1.5 rounded-full bg-indigo-300 shrink-0" />{pt}
                  </li>
                ))}
              </ul>
            </div>
          )}
          {backAnalogy && (
            <div className="bg-white/10 rounded-xl px-4 py-3 border border-white/20">
              <p className="text-xs font-bold text-indigo-200 uppercase tracking-widest mb-1">💡 Analogy</p>
              <p className="text-white text-sm italic">{backAnalogy}</p>
            </div>
          )}
          <p className="text-indigo-300 text-xs text-center mt-auto">Click to flip back</p>
        </div>
      </div>
    </div>
  );
}

// ─── Concept Map — keywords only, never analogy ───────────────────────────────
function TopicDiagram({ topic, keywords }) {
  const colors = ["#1025f9", "#6366f1", "#8b5cf6", "#06b6d4", "#0ea5e9", "#10b981", "#f59e0b", "#ef4444"];
  // Filter out anything that looks like a sentence (analogy guard)
  const safeKeywords = (keywords || []).filter((k) => k && k.split(" ").length <= 5);

  return (
    <div className="mt-6">
      <h3 className="text-sm font-semibold text-gray-500 uppercase tracking-widest mb-4">Concept Map</h3>
      <div className="flex flex-col items-center gap-0">
        {/* Root node */}
        <div className="bg-[#1025f9] text-white px-6 py-3 rounded-2xl font-bold text-base shadow-lg text-center max-w-xs">
          {topic}
        </div>
        {/* Connector line down */}
        <div className="w-0.5 h-6 bg-gray-300" />
        {/* Horizontal bar */}
        <div className="relative flex items-start justify-center gap-0">
          {safeKeywords.map((kw, i) => (
            <div key={i} className="flex flex-col items-center" style={{ minWidth: "100px", maxWidth: "140px" }}>
              <div className="w-0.5 h-5 bg-gray-300" />
              <div
                className="px-3 py-2 rounded-xl text-white text-xs font-medium shadow text-center w-full"
                style={{ backgroundColor: colors[i % colors.length] }}
              >
                {kw}
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

// ─── Section Block ─────────────────────────────────────────────────────────────
function Section({ icon, title, children, bg = "bg-white", border = "border-gray-100" }) {
  return (
    <div className={`${bg} border ${border} rounded-xl p-4 mb-3`}>
      <p className="text-xs font-bold text-gray-400 uppercase tracking-widest mb-2">{icon} {title}</p>
      {children}
    </div>
  );
}

// ─── Main Page ────────────────────────────────────────────────────────────────
export default function RecallCard() {
  const [tab, setTab]             = useState("flashcard");
  const [concept, setConcept]     = useState("");
  const [flashcard, setFlashcard] = useState(null);
  const [fcLoading, setFcLoading] = useState(false);
  const [summary, setSummary]     = useState(null);
  const [smLoading, setSmLoading] = useState(false);

  const getUserId = () => {
    try { return JSON.parse(localStorage.getItem("user") || "{}").id || "00000000-0000-0000-0000-000000000001"; }
    catch { return "00000000-0000-0000-0000-000000000001"; }
  };

  const handleFlashcard = async () => {
    if (!concept.trim()) return alert("Please enter a concept");
    setFcLoading(true); setFlashcard(null);
    try {
      const res = await axios.post(`${BASE_URL}/recall-cards/generate`, {
        user_id: getUserId(), topic: concept, keywords: [], diagram_image_url: "", analogy: "",
      });
      setFlashcard(res.data);
    } catch (err) { console.error(err); alert("Failed to generate flashcard."); }
    finally { setFcLoading(false); }
  };

  const handleSummary = async () => {
    if (!concept.trim()) return alert("Please enter a concept");
    setSmLoading(true); setSummary(null);
    try {
      const res = await axios.post(`${BASE_URL}/recall-cards/summary`, { topic: concept });
      setSummary(res.data);
    } catch (err) { console.error(err); alert("Failed to generate summary."); }
    finally { setSmLoading(false); }
  };

  const isLoading      = tab === "flashcard" ? fcLoading : smLoading;
  const handleGenerate = tab === "flashcard" ? handleFlashcard : handleSummary;

  return (
    <div className="min-h-screen bg-gradient-to-br from-[#f0f4ff] to-white flex flex-col">
      <Navbar />
      <motion.section className="flex-1 flex flex-col items-center px-6 py-12"
        initial={{ opacity: 0, y: 24 }} animate={{ opacity: 1, y: 0 }}>
        <h1 className="text-4xl font-bold text-[#1025f9] mb-2 text-center">Recall Card</h1>
        <p className="text-gray-500 max-w-xl text-center mb-8 text-sm">
          Generate visual flashcards or a structured summary with concept map for any topic.
        </p>

        {/* Tab Toggle */}
        <div className="flex bg-gray-100 rounded-xl p-1 mb-8 gap-1 w-full max-w-sm">
          {[{ key: "flashcard", label: "🃏 Flashcard" }, { key: "summary", label: "📊 Summary & Diagram" }].map(({ key, label }) => (
            <button key={key} onClick={() => setTab(key)}
              className={`flex-1 py-2 rounded-lg text-sm font-semibold transition-all ${tab === key ? "bg-white text-[#1025f9] shadow" : "text-gray-500 hover:text-gray-700"}`}>
              {label}
            </button>
          ))}
        </div>

        <div className="w-full max-w-2xl bg-white rounded-2xl shadow-lg p-6">
          <label className="block text-sm font-semibold text-gray-600 mb-1">Enter Topic / Concept</label>
          <div className="flex gap-3">
            <input type="text" placeholder="e.g., Neural Networks, Binary Search..."
              value={concept} onChange={(e) => setConcept(e.target.value)}
              onKeyDown={(e) => e.key === "Enter" && handleGenerate()}
              className="flex-1 px-4 py-2 border border-gray-200 rounded-xl focus:outline-none focus:ring-2 focus:ring-[#1025f9] text-sm" />
            <button onClick={handleGenerate} disabled={isLoading}
              className="bg-[#1025f9] text-white px-5 py-2 rounded-xl hover:bg-blue-700 transition text-sm font-semibold disabled:opacity-50">
              {isLoading ? "Generating..." : "Generate"}
            </button>
          </div>

          <AnimatePresence mode="wait">
            {/* ── Flashcard Tab ── */}
            {tab === "flashcard" && (
              <motion.div key="fc" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="mt-6">
                {flashcard ? (
                  <>
                    <p className="text-xs text-gray-400 text-center mb-3">Click the card to flip</p>
                    <FlipCard
                      frontTitle={flashcard.front_title}
                      frontSubtitle={flashcard.front_subtitle}
                      backDefinition={flashcard.back_definition}
                      backPoints={flashcard.back_points}
                      backAnalogy={flashcard.back_analogy}
                    />
                    {flashcard.keywords?.length > 0 && (
                      <div className="mt-5">
                        <p className="text-xs font-semibold text-gray-400 uppercase tracking-widest mb-2">Related Keywords</p>
                        <div className="flex flex-wrap gap-2">
                          {flashcard.keywords.map((kw, i) => (
                            <span key={i} className="bg-indigo-50 text-indigo-700 text-xs px-3 py-1 rounded-full font-medium border border-indigo-100">{kw}</span>
                          ))}
                        </div>
                      </div>
                    )}
                  </>
                ) : (
                  <div className="h-64 bg-gray-50 rounded-2xl flex flex-col items-center justify-center text-gray-300 text-sm gap-2">
                    <span className="text-4xl">🃏</span>Your flashcard will appear here
                  </div>
                )}
              </motion.div>
            )}

            {/* ── Summary Tab ── */}
            {tab === "summary" && (
              <motion.div key="sm" initial={{ opacity: 0, y: 12 }} animate={{ opacity: 1, y: 0 }} exit={{ opacity: 0 }} className="mt-6 space-y-3">
                {summary ? (
                  <>
                    {/* Overview */}
                    {summary.overview && (
                      <Section icon="📖" title="Overview" bg="bg-indigo-50" border="border-indigo-100">
                        <p className="text-sm text-indigo-900 leading-relaxed">{summary.overview}</p>
                      </Section>
                    )}

                    {/* Key Points */}
                    {summary.points?.length > 0 && (
                      <Section icon="📌" title="Key Points">
                        <ul className="space-y-2">
                          {summary.points.map((pt, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-gray-700">
                              <span className="mt-1.5 w-2 h-2 rounded-full bg-[#1025f9] shrink-0" />{pt}
                            </li>
                          ))}
                        </ul>
                      </Section>
                    )}

                    {/* Use Cases */}
                    {summary.use_cases?.length > 0 && (
                      <Section icon="🚀" title="Real-World Use Cases" bg="bg-emerald-50" border="border-emerald-100">
                        <ul className="space-y-1">
                          {summary.use_cases.map((uc, i) => (
                            <li key={i} className="flex items-start gap-2 text-sm text-emerald-800">
                              <span className="mt-1.5 w-2 h-2 rounded-full bg-emerald-500 shrink-0" />{uc}
                            </li>
                          ))}
                        </ul>
                      </Section>
                    )}

                    {/* Analogy */}
                    {summary.analogy && (
                      <div className="bg-indigo-50 border border-indigo-100 rounded-xl p-4 text-sm text-indigo-800">
                        <span className="font-semibold">💡 Analogy: </span>{summary.analogy}
                      </div>
                    )}

                    {/* Tip */}
                    {summary.tip && (
                      <div className="bg-amber-50 border border-amber-100 rounded-xl p-4 text-sm text-amber-800">
                        <span className="font-semibold">⚠️ Pro Tip: </span>{summary.tip}
                      </div>
                    )}

                    {/* Concept Map — keywords only */}
                    {summary.keywords?.length > 0 && (
                      <TopicDiagram topic={summary.topic || concept} keywords={summary.keywords} />
                    )}
                  </>
                ) : (
                  <div className="h-64 bg-gray-50 rounded-2xl flex flex-col items-center justify-center text-gray-300 text-sm gap-2">
                    <span className="text-4xl">📊</span>Summary and diagram will appear here
                  </div>
                )}
              </motion.div>
            )}
          </AnimatePresence>
        </div>
      </motion.section>
      <Footer />
    </div>
  );
}
