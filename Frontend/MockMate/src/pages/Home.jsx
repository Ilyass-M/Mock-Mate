import Navbar from "../components/Navbar"
import CVUpload from "../components/CVUpload"
import JobList from "../components/JobList"
import { ArrowRight, CheckCircle, FileText, Briefcase, MessageSquare } from "lucide-react"

const Home = () => {
  const user = JSON.parse(localStorage.getItem("user"))

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 w-full">
      <main className="w-full">
        {user && (
          <div className="w-full px-8 py-12">
            <div className="text-center mb-16">
              <div className="inline-block mb-4">
                <span className="inline-flex items-center px-4 py-2 rounded-full text-lg font-medium bg-blue-100 text-blue-800">
                  AI-Powered Interview Practice
                </span>
              </div>
              <h1 className="text-5xl font-extrabold tracking-tight text-gray-900 sm:text-6xl md:text-7xl">
                <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
                  MockMate
                </span>
                <span className="block mt-2">Ace Your Interviews</span>
              </h1>
              <p className="mt-8 max-w-3xl mx-auto text-2xl text-gray-500">
                Upload your CV and start practicing interviews with our AI-powered mock interviews. Get personalized
                feedback to improve your skills.
              </p>
              <div className="mt-12">
                <a
                  href="#upload-cv"
                  className="inline-flex items-center justify-center px-8 py-4 border border-transparent text-lg font-medium rounded-lg shadow-lg text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 transform hover:-translate-y-1"
                >
                  <FileText className="h-6 w-6 mr-3" />
                  Get Started
                </a>
              </div>
            </div>

            <div className="grid grid-cols-1 lg:grid-cols-2 gap-12 mb-20" id="upload-cv">
              <div className="bg-white rounded-2xl shadow-xl overflow-hidden transform transition-all duration-300 hover:shadow-2xl">
                <div className="p-10">
                  <div className="flex items-center justify-between mb-8">
                    <h2 className="text-3xl font-bold text-gray-900">Upload Your CV</h2>
                    <div className="h-16 w-16 rounded-full bg-blue-100 flex items-center justify-center">
                      <FileText className="h-8 w-8 text-blue-600" />
                    </div>
                  </div>

                  <CVUpload />
                </div>
              </div>

              <div className="bg-white rounded-2xl shadow-xl overflow-hidden transform transition-all duration-300 hover:shadow-2xl">
                <div className="p-10">
                  <h2 className="text-3xl font-bold text-gray-900 mb-8 flex items-center">
                    <CheckCircle className="h-8 w-8 text-blue-600 mr-3" />
                    How It Works
                  </h2>
                  <div className="space-y-10">
                    <div className="flex items-start">
                      <div className="flex-shrink-0">
                        <div className="flex items-center justify-center h-12 w-12 rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg text-xl font-bold">
                          1
                        </div>
                      </div>
                      <div className="ml-6">
                        <h3 className="text-xl font-bold text-gray-900">Upload Your CV</h3>
                        <p className="mt-2 text-lg text-gray-500">
                          Start by uploading your CV in PDF format. Our system will analyze your skills and experience
                          to tailor the interview questions.
                        </p>
                      </div>
                    </div>

                    <div className="flex items-start">
                      <div className="flex-shrink-0">
                        <div className="flex items-center justify-center h-12 w-12 rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg text-xl font-bold">
                          2
                        </div>
                      </div>
                      <div className="ml-6">
                        <h3 className="text-xl font-bold text-gray-900">Browse Jobs</h3>
                        <p className="mt-2 text-lg text-gray-500">
                          Explore available job positions and select the one that matches your career goals for targeted
                          interview practice.
                        </p>
                      </div>
                    </div>

                    <div className="flex items-start">
                      <div className="flex-shrink-0">
                        <div className="flex items-center justify-center h-12 w-12 rounded-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white shadow-lg text-xl font-bold">
                          3
                        </div>
                      </div>
                      <div className="ml-6">
                        <h3 className="text-xl font-bold text-gray-900">Start Interview</h3>
                        <p className="mt-2 text-lg text-gray-500">
                          Begin the AI-powered mock interview session. Receive real-time feedback and detailed analysis
                          of your performance.
                        </p>
                      </div>
                    </div>
                  </div>

                  <div className="mt-10 text-center">
                    <a
                      href="#job-list"
                      className="inline-flex items-center px-6 py-3 border border-transparent text-lg font-medium rounded-lg text-blue-700 bg-blue-100 hover:bg-blue-200 transition-colors duration-150 ease-in-out"
                    >
                      Browse Available Jobs
                      <ArrowRight className="ml-2 -mr-1 h-5 w-5" />
                    </a>
                  </div>
                </div>
              </div>
            </div>

            <div className="mb-20" id="job-list">
              <div className="text-center mb-12">
                <h2 className="text-4xl font-bold text-gray-900">Available Job Positions</h2>
                <p className="mt-4 text-2xl text-gray-500">
                  Select a job position to practice your interview skills
                </p>
              </div>
              <JobList />
            </div>

            <div className="bg-white rounded-2xl shadow-xl p-12 mb-20">
              <div className="text-center mb-12">
                <h2 className="text-4xl font-bold text-gray-900">Why Choose MockMate?</h2>
                <p className="mt-4 text-2xl text-gray-500">
                  Our platform offers unique advantages to help you succeed
                </p>
              </div>

              <div className="grid grid-cols-1 md:grid-cols-3 gap-10">
                <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-8 rounded-xl">
                  <div className="h-16 w-16 rounded-full bg-blue-100 flex items-center justify-center mb-6">
                    <MessageSquare className="h-8 w-8 text-blue-600" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">AI-Powered Feedback</h3>
                  <p className="text-lg text-gray-500">
                    Get instant, detailed feedback on your interview performance with actionable insights.
                  </p>
                </div>

                <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-8 rounded-xl">
                  <div className="h-16 w-16 rounded-full bg-blue-100 flex items-center justify-center mb-6">
                    <Briefcase className="h-8 w-8 text-blue-600" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">Industry-Specific Questions</h3>
                  <p className="text-lg text-gray-500">
                    Practice with questions tailored to your industry, job role, and experience level.
                  </p>
                </div>

                <div className="bg-gradient-to-br from-blue-50 to-indigo-50 p-8 rounded-xl">
                  <div className="h-16 w-16 rounded-full bg-blue-100 flex items-center justify-center mb-6">
                    <CheckCircle className="h-8 w-8 text-blue-600" />
                  </div>
                  <h3 className="text-2xl font-bold text-gray-900 mb-4">Skill Improvement</h3>
                  <p className="text-lg text-gray-500">
                    Track your progress over time and see measurable improvements in your interview skills.
                  </p>
                </div>
              </div>
            </div>
          </div>
        )}

        {!user && (
          <div className="w-full px-8 py-20">
            <div className="lg:grid lg:grid-cols-2 lg:gap-20 items-center">
              <div>
                <div className="inline-block mb-6">
                  <span className="inline-flex items-center px-4 py-2 rounded-full text-lg font-medium bg-blue-100 text-blue-800">
                    AI-Powered Interview Practice
                  </span>
                </div>
                <h1 className="text-5xl font-extrabold tracking-tight text-gray-900 sm:text-6xl md:text-7xl">
                  <span className="block text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-indigo-600">
                    MockMate
                  </span>
                  <span className="block mt-2">Practice Makes Perfect</span>
                </h1>
                <p className="mt-8 text-2xl text-gray-500">
                  Sign in to start practicing interviews with our AI-powered mock interview system. Get personalized
                  feedback and improve your chances of landing your dream job.
                </p>
                <div className="mt-12 flex gap-6">
                  <a
                    href="/login"
                    className="inline-flex items-center px-8 py-4 border border-transparent text-lg font-medium rounded-lg shadow-lg text-white bg-gradient-to-r from-blue-600 to-indigo-600 hover:from-blue-700 hover:to-indigo-700 transition-all duration-200 transform hover:-translate-y-1"
                  >
                    Sign In
                  </a>
                  <a
                    href="/register"
                    className="inline-flex items-center px-8 py-4 border border-gray-300 text-lg font-medium rounded-lg shadow-lg text-gray-700 bg-white hover:bg-gray-50 transition-all duration-200"
                  >
                    Create Account
                  </a>
                </div>
              </div>
              <div className="mt-16 lg:mt-0">
                <div className="bg-white rounded-2xl shadow-xl overflow-hidden">
                  <div className="relative aspect-[4/3] bg-gradient-to-br from-blue-600 to-indigo-600">
                    <img
                      src="/placeholder.svg?height=400&width=600"
                      alt="MockMate Interview Platform"
                      className="absolute inset-0 w-full h-full object-cover mix-blend-overlay opacity-20"
                    />
                    <div className="absolute inset-0 flex items-center justify-center">
                      <div className="text-center text-white p-12">
                        <h2 className="text-3xl font-bold mb-6">Prepare for Success</h2>
                        <p className="text-xl">
                          Our AI-powered platform has helped thousands of job seekers improve their interview skills and
                          land their dream jobs.
                        </p>
                      </div>
                    </div>
                  </div>
                  <div className="p-12">
                    <div className="flex items-center space-x-6 mb-8">
                      <div className="flex -space-x-4">
                        <img
                          className="h-12 w-12 rounded-full ring-2 ring-white"
                          src="/placeholder.svg?height=48&width=48"
                          alt="User"
                        />
                        <img
                          className="h-12 w-12 rounded-full ring-2 ring-white"
                          src="/placeholder.svg?height=48&width=48"
                          alt="User"
                        />
                        <img
                          className="h-12 w-12 rounded-full ring-2 ring-white"
                          src="/placeholder.svg?height=48&width=48"
                          alt="User"
                        />
                      </div>
                      <span className="text-lg text-gray-500">Join 10,000+ users already practicing</span>
                    </div>
                    <div className="space-y-6">
                      <div className="flex items-start">
                        <CheckCircle className="h-6 w-6 text-green-500 mt-1 mr-3" />
                        <p className="text-lg text-gray-600">Personalized interview questions based on your CV</p>
                      </div>
                      <div className="flex items-start">
                        <CheckCircle className="h-6 w-6 text-green-500 mt-1 mr-3" />
                        <p className="text-lg text-gray-600">Detailed feedback on your answers and performance</p>
                      </div>
                      <div className="flex items-start">
                        <CheckCircle className="h-6 w-6 text-green-500 mt-1 mr-3" />
                        <p className="text-lg text-gray-600">Practice for specific job positions and industries</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </main>

      <footer className="bg-white border-t border-gray-200 mt-20">
        <div className="w-full px-8 py-12">
          <div className="md:flex md:items-center md:justify-between">
            <div className="flex justify-center md:justify-start">
              <h2 className="text-3xl font-bold text-gray-900">MockMate</h2>
            </div>
            <div className="mt-8 md:mt-0">
              <p className="text-center md:text-right text-lg text-gray-500">
                &copy; {new Date().getFullYear()} MockMate. All rights reserved.
              </p>
            </div>
          </div>
        </div>
      </footer>
    </div>
  )
}

export default Home
