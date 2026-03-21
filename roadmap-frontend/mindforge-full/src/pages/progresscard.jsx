import React from "react";
import { motion } from "framer-motion";
import Navbar from "../components/DashNav";
import Footer from "../components/Footer";
import ProgressCard from "../components/ProgressCard"; // ✅ Import actual progress card

export default function ProgressCardPage() {
  // 🔹 Later you can replace "123" with the logged-in user's real ID from auth
  const userId = "123";

  return (
    <div className="min-h-screen bg-gradient-to-br from-secondary to-white text-dark flex flex-col">
      <Navbar />

      <motion.section
        className="flex-1 flex flex-col items-center justify-start text-center px-6 py-20"
        initial={{ opacity: 0, y: 30 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.6 }}
      >
        <h1 className="text-4xl md:text-5xl font-bold text-primary mb-4">
          Progress Card
        </h1>
        <p className="text-lg text-gray-700 max-w-2xl mb-6">
          Track your learning journey, see skills mastered, and identify areas
          needing more attention.
        </p>

        {/* ✅ Actual Progress Card Component */}
        <div className="w-full max-w-4xl bg-white p-6 rounded-xl shadow-lg text-left">
          <ProgressCard userId={userId} />
        </div>
      </motion.section>

      <Footer />
    </div>
  );
}
