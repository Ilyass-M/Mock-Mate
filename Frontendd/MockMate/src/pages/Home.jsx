import React from "react";
import CVUpload from "../components/CVUpload";
import JobList from "../components/JobList";
import { ArrowRight, CheckCircle, FileText, Briefcase, MessageSquare } from "lucide-react";
import { useAuth } from "../context/AuthContext";
import { Link } from "react-router-dom";

const Home = () => {
  const { user } = useAuth();

  return (
    <div className="container mx-auto">
      <section className="py-16 px-6 sm:px-10 md:px-20 bg-gradient-to-br from-slate-50 to-blue-50 text-center">
        <div className="max-w-5xl mx-auto">
          <span className="inline-block bg-blue-100 text-blue-800 text-sm font-medium px-4 py-2 rounded-full mb-4">
            AI-Powered Interview Practice
          </span>
          <h1 className="text-4xl sm:text-5xl md:text-6xl font-extrabold text-gray-900 leading-tight">
            <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">MockMate</span>
            <div className="mt-2">Ace Your Interviews with Confidence</div>
          </h1>
          <p className="mt-6 text-lg sm:text-xl text-gray-600 max-w-3xl mx-auto">
            Upload your CV and practice interviews with smart, adaptive AI. Get feedback and grow your confidence.
          </p>
          <a
            href="#upload"
            className="inline-flex mt-8 px-8 py-4 bg-indigo-600 hover:bg-indigo-700 text-white font-medium rounded-xl shadow-lg transition transform hover:-translate-y-1"
          >
            <FileText className="w-5 h-5 mr-2" />
            Get Started
          </a>
        </div>
      </section>

      {user && (
        <section id="upload" className="py-16 px-6 sm:px-10 md:px-20">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-12 max-w-6xl mx-auto">
            <div className="bg-white p-8 rounded-3xl shadow-lg transition hover:shadow-2xl">
              {/* <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold text-gray-900">Upload Your CV</h2>
                <div className="h-12 w-12 bg-blue-100 rounded-full flex items-center justify-center">
                  <FileText className="w-6 h-6 text-blue-600" />
                </div>
              </div> */}
              <CVUpload />
            </div>

            <div className="bg-white p-8 rounded-3xl shadow-lg transition hover:shadow-2xl">
              <h2 className="text-2xl font-bold text-gray-900 flex items-center mb-6">
                <CheckCircle className="w-6 h-6 text-blue-600 mr-2" />
                How It Works
              </h2>
              <div className="space-y-6 text-left">
                {[
                  {
                    step: "1",
                    title: "Upload Your CV",
                    description:
                      "Upload your CV. To register as a valid candidate to start practicing on our AI which analyzes your experiences and projects, and prepares questions tailored to your skills.",
                  },
                  {
                    step: "2",
                    title: "Select a Job",
                    description:
                      "Pick a job role that aligns with your interests and get questions customized to that position.",
                  },
                  {
                    step: "3",
                    title: "Start Interview",
                    description:
                      "Begin your interview. Get real-time evaluation, feedback, and improvement tips.",
                  },
                ].map(({ step, title, description }) => (
                  <div key={step} className="flex items-start">
                    <div className="flex items-center px-4 justify-center w-10 h-10 rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white font-bold">
                      {step}
                    </div>
                    <div className="ml-4">
                    <h3 className="text-lg font-semibold text-gray-900">{title}</h3>
                      <p className="text-gray-600 mt-1 text-sm">{description}</p>
                    </div>
                  </div>
                ))}
              </div>
              <div className="mt-6 text-center">
                <a
                  href="#jobs"
                  className="inline-flex items-center px-6 py-3 text-indigo-700 bg-indigo-100 hover:bg-indigo-200 rounded-lg transition"
                >
                  Browse Jobs
                  <ArrowRight className="ml-2 w-4 h-4" />
                </a>
              </div>
            </div>
          </div>
        </section>
      )}

      {user && (
        <section id="jobs" className="py-16 px-6 sm:px-10 md:px-20 bg-white">
          <div className="text-center mb-12">            <h2 className="text-3xl font-bold text-gray-900">Available Job Positions</h2>
            <p className="text-gray-500 mt-2 text-lg">Choose a position and practice targeted questions</p>
          </div>
          <JobList limit={3} />
          <div className="flex justify-center mt-8">
            <Link 
              to="/all-jobs"
               
              className=" inline-flex items-center px-6 py-3 border border-transparent text-base font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
            >
              See More Jobs
              <ArrowRight className="ml-2 w-5 h-5" />
            </Link>
          </div>
        </section>
      )}

      <section className="py-16 px-6 sm:px-10 md:px-20 bg-gradient-to-tr from-white to-slate-100">
        <div className="text-center mb-12">
          <h2 className="text-3xl font-bold text-gray-900">Why Choose MockMate?</h2>
          <p className="text-gray-500 mt-2 text-lg">Built for results, driven by AI</p>
        </div>
        <div className="grid gap-10 grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 max-w-6xl mx-auto">
          {[
            {
              icon: MessageSquare,
              title: "AI Feedback",
              description: "Instant, detailed feedback on your answers — so you know exactly where to improve.",
            },
            {
              icon: Briefcase,
              title: "Job-Relevant",
              description: "Questions tailored to job roles, industries, and skill levels.",
            },
            {
              icon: CheckCircle,
              title: "Track Growth",
              description: "Monitor progress and watch your confidence rise with every mock session.",
            },
          ].map((feature, index) => (
            <div key={index} className="bg-white p-8 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300">
              <div className="h-12 w-12 bg-indigo-100 rounded-xl flex items-center justify-center mb-6">
                <feature.icon className="h-6 w-6 text-indigo-600" />
              </div>
              <h3 className="text-xl font-bold text-gray-900 mb-3">{feature.title}</h3>
              <p className="text-gray-600">{feature.description}</p>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
};

export default Home;
