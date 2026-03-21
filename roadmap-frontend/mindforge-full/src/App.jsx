import { BrowserRouter as Router, Routes, Route } from "react-router-dom";
import "./index.css";
import LandingPage from "./pages/LandingPage";
import LoginPage from "./pages/login";
import SignupPage from "./pages/signup";
import Dashboard from "./pages/Dashboard";
import Roadmap from "./pages/roadmap";
import ConfusionDetector from "./pages/ConfusionDetector";
import RecallCard from "./pages/recallcard";
import ProgressCard from "./pages/progresscard";
import LearnQuiz from "./pages/LearnQuiz";
import Quiz from "./pages/quiz";
import RoadmapHistory from "./pages/roadmap-history";
import ConfusionDetectorHistory from "./pages/confusiondetector-history";
import RecallCardHistory from "./pages/recallcard-history";
import ProgressCardHistory from "./pages/progresscard-history";
// import LearnQuizHistory from "./pages/learn&quiz"
import QuizHistory from "./pages/quiz-history";
import QuizPage from "./components/QuizPage";

export default function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<LandingPage />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/signup" element={<SignupPage />} />
        <Route path="/dashboard" element={<Dashboard />} />
        <Route path="/roadmap" element={<Roadmap />} />
        <Route path="/confusion-detector" element={<ConfusionDetector />} />
        <Route path="/recallcard" element={<RecallCard />} />
        <Route path="/progresscard" element={<ProgressCard />} />
        <Route path="/learn&quiz" element={<LearnQuiz/>} />
        <Route path="/quiz" element={<Quiz />} />
        <Route path="/roadmap-history" element={<RoadmapHistory />} />
        <Route path="/quiz-history" element={<QuizHistory />} />
        <Route path="/progresscard-history" element={<ProgressCardHistory />} />
        <Route path="/recallcard-history" element={<RecallCardHistory />} />
        <Route path="/confusiondetector-history" element={<ConfusionDetectorHistory />} />
        <Route path="/quiz/:topic" element={<QuizPage />} />
      </Routes>
    </Router>
  );
}
