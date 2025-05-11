import React, { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import authService from "../services/authService";

const Register = () => {
  const navigate = useNavigate();
  const [formData, setFormData] = useState({
    email: "",
    username: "",
    fullname: "",
    phone_number: "",
    password: "",
    is_recruiter: false,
    is_candidate: false,
  });
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const handleChange = (e) => {
    const { name, value, type, checked } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: type === "checkbox" ? checked : value,
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setError("");
    setLoading(true);

    if (!formData.is_recruiter && !formData.is_candidate) {
      setError("Please select at least one role");
      setLoading(false);
      return;
    }

    try {
      await authService.register(formData);
      navigate("/login");
    } catch (err) {
      setError(err.error || "An error occurred during registration");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="flex flex-col items-center justify-center w-full min-h-screen px-6 py-12 bg-gradient-to-br from-blue-100 to-indigo-100">
      <div className="w-full max-w-3xl bg-white rounded-3xl shadow-2xl p-10 sm:p-12">
        <h2 className="text-4xl font-bold text-center text-gray-900 mb-4">Create Your Account</h2>
        <p className="text-center text-gray-500 mb-8">Join MockMate and start practicing today</p>

        {error && (
          <div className="mb-6 bg-red-100 border-l-4 border-red-500 text-red-700 p-4 rounded">
            {error}
          </div>
        )}

        <form className="space-y-6" onSubmit={handleSubmit}>
          <div className="grid sm:grid-cols-2 gap-6">
            <input
              type="text"
              name="fullname"
              placeholder="Full Name"
              className="p-3 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500"
              value={formData.fullname}
              onChange={handleChange}
              required
            />
            <input
              type="text"
              name="username"
              placeholder="Username"
              className="p-3 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500"
              value={formData.username}
              onChange={handleChange}
              required
            />
          </div>

          <input
            type="email"
            name="email"
            placeholder="Email Address"
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500"
            value={formData.email}
            onChange={handleChange}
            required
          />

          <input
            type="tel"
            name="phone_number"
            placeholder="Phone Number"
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500"
            value={formData.phone_number}
            onChange={handleChange}
            required
          />

          <input
            type="password"
            name="password"
            placeholder="Password"
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-indigo-500 focus:border-indigo-500"
            value={formData.password}
            onChange={handleChange}
            required
          />

          <div className="flex gap-6 flex-col sm:flex-row">
            <label className="flex items-center space-x-2 text-sm font-medium text-gray-700">
              <input
                type="checkbox"
                name="is_candidate"
                checked={formData.is_candidate}
                onChange={handleChange}
              />
              <span>Candidate</span>
            </label>
            <label className="flex items-center space-x-2 text-sm font-medium text-gray-700">
              <input
                type="checkbox"
                name="is_recruiter"
                checked={formData.is_recruiter}
                onChange={handleChange}
              />
              <span>Recruiter</span>
            </label>
          </div>

          <button
            type="submit"
            disabled={loading}
            className="w-full py-3 px-6 font-medium text-white bg-indigo-600 hover:bg-indigo-700 rounded-lg shadow transition disabled:opacity-50"
          >
            {loading ? "Creating account..." : "Create Account"}
          </button>
        </form>

        <div className="mt-6 text-center text-sm text-gray-600">
          Already have an account?{" "}
          <Link to="/login" className="text-indigo-600 hover:text-indigo-500 font-medium">
            Sign in here
          </Link>
        </div>
      </div>
    </div>
  );
};

export default Register;
