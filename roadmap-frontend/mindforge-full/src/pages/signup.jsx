import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import { toast, ToastContainer } from "react-toastify";
import "react-toastify/dist/ReactToastify.css";
import { api } from "../services/api";

export default function SignupPage() {
  const [name, setName]             = useState("");
  const [email, setEmail]           = useState("");
  const [password, setPassword]     = useState("");
  const [careerGoal, setCareerGoal] = useState("");
  const [loading, setLoading]       = useState(false);
  const navigate = useNavigate();

  const handleSignup = async () => {
    if (!name || !email || !password) {
      toast.error("Please fill in all fields");
      return;
    }

    setLoading(true);
    try {
      const res = await api.signup({
        name,
        email,
        password,
        career_goal: careerGoal || "",
      });

      // Handle both wrapped { data: ... } and unwrapped responses
      const payload = res?.data ?? res;

      if (payload?.access_token) {
        localStorage.setItem("token", payload.access_token);
        if (payload.user) {
          localStorage.setItem(
            "user",
            JSON.stringify({ ...payload.user, career_goal: careerGoal || "" })
          );
        }
        toast.success("Signup successful!");
        setTimeout(() => navigate("/dashboard"), 1500);
      } else if (payload?.detail) {
        toast.error(typeof payload.detail === "string" ? payload.detail : "Signup failed.");
      } else {
        toast.error("Signup failed. Try again.");
      }
    } catch (err) {
      // Axios puts error response body in err.response.data
      const detail = err?.response?.data?.detail;
      if (detail) {
        toast.error(typeof detail === "string" ? detail : "Signup failed.");
      } else {
        toast.error("Signup failed. Please try again.");
      }
      console.error("Signup error:", err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen flex items-center justify-center bg-secondary">
      <div className="bg-white p-8 rounded-md shadow-lg w-full max-w-md">
        <h2 className="text-xl font-bold mb-4 text-primary">Create Account</h2>

        <input
          type="text"
          placeholder="Full Name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          className="w-full mb-4 p-2 border border-border rounded"
        />
        <input
          type="email"
          placeholder="Email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          className="w-full mb-4 p-2 border border-border rounded"
        />
        <input
          type="password"
          placeholder="Password"
          value={password}
          onChange={(e) => setPassword(e.target.value)}
          className="w-full mb-4 p-2 border border-border rounded"
        />
        <input
          type="text"
          placeholder="Career Goal (e.g. Full Stack Developer, Data Scientist)"
          value={careerGoal}
          onChange={(e) => setCareerGoal(e.target.value)}
          className="w-full mb-6 p-2 border border-border rounded"
        />

        <button
          onClick={handleSignup}
          disabled={loading}
          className="w-full bg-primary text-white py-2 rounded hover:bg-blue-600 disabled:opacity-50"
        >
          {loading ? "Creating account..." : "Sign Up"}
        </button>

        <p className="text-center mt-4 text-sm text-gray-600">
          Already have an account?{" "}
          <Link to="/login" className="text-primary hover:underline">
            Login
          </Link>
        </p>

        <ToastContainer position="top-center" autoClose={1500} />
      </div>
    </div>
  );
}