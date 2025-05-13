import { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';
import { FaSpinner } from 'react-icons/fa';
import { AiOutlineCheckCircle, AiOutlineCloseCircle } from 'react-icons/ai';

const InterviewInterface = () => {
  const { id } = useParams();
  const { user } = useAuth();
  const navigate = useNavigate();
  const [connected, setConnected] = useState(true);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [answer, setAnswer] = useState('');
  const [evaluations, setEvaluations] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [answeredQuestions, setAnsweredQuestions] = useState(0);
  const [interviewComplete, setInterviewComplete] = useState(false);
  const [jobDetails, setJobDetails] = useState(null);
  const [assessment, setAssessment] = useState(null);
  const [startInterview_var, setStartInterview_var] = useState(false);
  useEffect(() => {
    const fetchJobDetails = async () => {
      try {
        setIsLoading(true);
        const response = await fetch(`http://localhost:8000/api/JobDescription/${id}/`, {
          credentials: 'include'
        });

        if (!response.ok) {
          throw new Error('Failed to fetch job details');
        }

        const data = await response.json();
        setJobDetails(data);
        // Reset the interview state
        setStartInterview_var(false);
        setCurrentQuestion(null);
        setEvaluations([]);
        setAnswer('');
        setAnsweredQuestions(0);
        setInterviewComplete(false);
        setResult(null);
        setIsLoading(false);
      } catch (error) {
        setError(error.message);
        setConnected(false);
        setIsLoading(false);
      }
    };

    fetchJobDetails();
  }, [id]);
  const requestNextQuestion = async () => {
    try {
      setIsLoading(true);
      const context = jobDetails ?
        `Job title: ${jobDetails.title}, Job description: ${jobDetails.description}` :
        `Technical interview for job ID: ${id}`;

      const response = await fetch('http://localhost:8000/api/gemini/question/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          context: context,
          previousQuestions: evaluations.map(ev => ev.question),
          difficulty: evaluations.length > 0 ? 'intermediate' : 'beginner',
          job_id: id,
          candidate_id: user?.id // Send the user ID if available
        }),
        credentials: 'include'
      }); if (!response.ok) {
        throw new Error('Failed to generate question');
      }

      const data = await response.json();
      setCurrentQuestion({
        id: data.id,
        question_text: data.question || "Tell me about your experience with React?",
        category: data.category || "Frontend Development",
        difficulty: data.difficulty || "Intermediate"
      });

      // Store the assessment ID for later API calls
      if (data.assessment_id) {
        setAssessment(data.assessment_id);
      } else if (data.assessment && data.assessment.id) {
        setAssessment(data.assessment.id);
      }

      setIsLoading(false);
    } catch (error) {
      setError('Error generating question: ' + error.message);
      setIsLoading(false);
    }
  };
  const submitAnswer = async () => {
    if (!currentQuestion || !answer.trim()) return;

    try {
      setIsLoading(true);
      const response = await fetch('http://localhost:8000/api/gemini/evaluate/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          question_id: currentQuestion.id,
          question: currentQuestion.question_text,
          answer: answer.trim(),
          context: jobDetails ? jobDetails.description : '',
          assessment_id: assessment
        }),
        credentials: 'include'
      }); if (!response.ok) {
        throw new Error('Failed to evaluate answer');
      }

      const data = await response.json();
      const evaluation = {
        question: currentQuestion.question_text,
        answer: answer.trim(),
        similarity_score: data.score || 0.75,
        feedback: data.feedback || "Good answer! You demonstrated knowledge of the subject.",
        id: currentQuestion.id,
        question_id: data.question_id || currentQuestion.id,
        assessment_id: data.assessment_id || assessment
      };

      setEvaluations(prev => [...prev, evaluation]);
      setAnsweredQuestions(prev => prev + 1);
      setAnswer('');
      setCurrentQuestion(null);
      setIsLoading(false);

      if (answeredQuestions + 1 >= 5) {
        finishInterview();
      }
    } catch (error) {
      setError('Error evaluating answer: ' + error.message);
      setIsLoading(false);
    }
  }; const finishInterview = async () => {
    try {
      setIsLoading(true);
      // Only make API call if there are evaluations
      if (evaluations.length === 0) {
        setError('Please answer at least one question before finishing the interview.');
        setIsLoading(false);
        return;
      }

      const response = await fetch('http://localhost:8000/api/gemini/result/', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          evaluations: evaluations,
          jobDetails: jobDetails,
          assessment_id: assessment,
          candidate_id: user?.id
        }),
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error('Failed to generate final result');
      }

      const data = await response.json();
      setResult({
        decision: data.decision || "Hire",
        probability: data.probability || [0.2, 0.8],
        summary: data.summary || "The candidate demonstrated good knowledge of the required skills."
      });

      setInterviewComplete(true);
      setIsLoading(false);
    } catch (error) {
      setError('Error generating result: ' + error.message);
      setIsLoading(false);
    }
  }; const startInterview = () => {
    setStartInterview_var(true);
    requestNextQuestion();
  };

  // Function to get text color based on score
  const _getScoreColor = (score) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (!connected) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
        <div className="w-full max-w-2xl bg-white rounded-lg shadow-md p-6">          <h1 className="text-2xl font-bold text-gray-800 mb-4">Interview System</h1>
          <p className="text-gray-600 mb-4">Unable to connect to interview session.</p>
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}          <button
            onClick={() => navigate('/')}
            className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors font-medium flex items-center justify-center"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M9.707 14.707a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 1.414L7.414 9H15a1 1 0 110 2H7.414l2.293 2.293a1 1 0 010 1.414z" clipRule="evenodd" />
            </svg>
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }
  if (interviewComplete && result) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
        <div className="w-full max-w-3xl bg-white rounded-lg shadow-lg p-6 border border-gray-200">
          <h1 className="text-2xl font-bold text-gray-800 mb-6 pb-2 border-b border-gray-200 flex items-center">
            <svg xmlns="http://www.w3.org/2000/svg" className="h-7 w-7 mr-3 text-indigo-600" viewBox="0 0 20 20" fill="currentColor">
              <path fillRule="evenodd" d="M6.267 3.455a3.066 3.066 0 001.745-.723 3.066 3.066 0 013.976 0 3.066 3.066 0 001.745.723 3.066 3.066 0 012.812 2.812c.051.643.304 1.254.723 1.745a3.066 3.066 0 010 3.976 3.066 3.066 0 00-.723 1.745 3.066 3.066 0 01-2.812 2.812 3.066 3.066 0 00-1.745.723 3.066 3.066 0 01-3.976 0 3.066 3.066 0 00-1.745-.723 3.066 3.066 0 01-2.812-2.812 3.066 3.066 0 00-.723-1.745 3.066 3.066 0 010-3.976 3.066 3.066 0 00.723-1.745 3.066 3.066 0 012.812-2.812zm7.44 5.252a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
            </svg>
            Interview Complete
          </h1>

          <div className="mb-6 p-5 rounded-lg bg-gradient-to-r from-indigo-50 to-blue-50 border border-indigo-100 shadow-sm">
            <h2 className="text-xl font-semibold mb-3 text-gray-800 flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 text-indigo-600" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-9.293a1 1 0 00-1.414-1.414L9 10.586 7.707 9.293a1 1 0 00-1.414 1.414l2 2a1 1 0 001.414 0l4-4z" clipRule="evenodd" />
              </svg>
              Results
            </h2>
            <div className="bg-white p-4 rounded-md shadow-sm">
              <p className="text-lg mb-3 flex items-center">
                <span className="font-medium mr-2">Decision:</span>
                <span
                  className={
                    result.decision === 'Hire'
                      ? 'text-green-600 font-bold bg-green-50 px-3 py-1 rounded-full'
                      : 'text-red-600 font-bold bg-red-50 px-3 py-1 rounded-full'
                  }
                >
                  {result.decision}
                </span>
              </p>
              <p className="text-lg mb-3 flex items-center">
                <span className="font-medium mr-2">Confidence:</span>
                <span className="text-indigo-600 font-semibold">{Math.round(result.probability[1] * 100)}%</span>
              </p>
              {result.summary && (
                <div className="mt-4 p-3 bg-white rounded">
                  <h3 className="font-medium mb-1">Summary:</h3>
                  <p className="text-gray-700">{result.summary}</p>
                </div>
              )}
            </div>

            <div className="mb-6">
              <h2 className="text-xl font-semibold mb-2">Performance Summary</h2>
              <p className="text-gray-700">
                You answered {answeredQuestions} questions in this interview.
              </p>
              <div className="mt-4">
                <h3 className="font-medium mb-2">Answer Evaluations:</h3>
                {evaluations.length > 0 ? (
                  <ul className="space-y-4">
                    {evaluations.map((evaluation, index) => (
                      <li
                        key={index}
                        className="border rounded-md p-4"
                      >
                        <div className="flex justify-between items-center border-b pb-2 mb-2">
                          <span className="font-medium">Question {index + 1}</span>
                        </div>
                        <p className="text-sm mb-2"><span className="font-medium">Q:</span> {evaluation.question}</p>
                        <p className="text-sm mb-2"><span className="font-medium">A:</span> {evaluation.answer}</p>
                        {evaluation.feedback && (
                          <p className="text-sm italic text-gray-600"><span className="font-medium">Feedback:</span> {evaluation.feedback}</p>
                        )}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-gray-500 italic">No evaluations available</p>
                )}
              </div>
            </div>        <div className="flex justify-center">
              <button
                onClick={() => navigate('/dashboard')}
                className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors font-medium flex items-center justify-center"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M9.707 14.707a1 1 0 01-1.414 0l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 1.414L7.414 9H15a1 1 0 110 2H7.414l2.293 2.293a1 1 0 010 1.414z" clipRule="evenodd" />
                </svg>
                Return to Dashboard
              </button>
            </div>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-3xl bg-white rounded-lg shadow-lg p-6 border border-gray-200">
        <div className="flex justify-between items-center mb-6 pb-4 border-b border-gray-200">
          <h1 className="text-2xl font-bold text-gray-800">AI Interview Session</h1>
          <div className="text-sm text-gray-600 bg-gray-100 px-3 py-1 rounded-full">{user?.email}</div>
        </div>

        {error && (
          <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
            {error}
            <button
              className="ml-2 text-red-700 underline"
              onClick={() => setError(null)}
            >
              Dismiss
            </button>
          </div>
        )}        {!currentQuestion && !isLoading && (
          <div className="text-center py-8">
            <h2 className="text-xl font-semibold mb-4">Ready to Start Your AI-Powered Interview?</h2>
            <p className="text-gray-600 mb-6">
              You'll be asked a series of questions generated by AI, tailored to the job description.
              Each answer will be evaluated by the AI with detailed feedback.
            </p>
            {!startInterview_var ? (<button
              onClick={startInterview}
              className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors font-medium flex items-center justify-center mx-auto"
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM9.555 7.168A1 1 0 008 8v4a1 1 0 001.555.832l3-2a1 1 0 000-1.664l-3-2z" clipRule="evenodd" />
              </svg>
              Start Interview
            </button>
            ) : (
              <div className="flex flex-col space-y-3 items-center">                <button
                onClick={requestNextQuestion}
                className="px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors font-medium flex items-center justify-center"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M10 3a1 1 0 011 1v5h5a1 1 0 110 2h-5v5a1 1 0 11-2 0v-5H4a1 1 0 110-2h5V4a1 1 0 011-1z" clipRule="evenodd" />
                </svg>
                Next Question
              </button>
                {evaluations.length > 0 && (
                  <button
                    onClick={finishInterview}
                    className="px-6 py-2 border border-gray-300 text-white rounded-md hover:bg-gray-100 transition-colors font-medium flex items-center justify-center"
                  >
                    <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                      <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                    </svg>
                    Finish Interview
                  </button>
                )}
              </div>
            )}
          </div>
        )}

        {isLoading && (
          <div className="flex flex-col items-center justify-center py-12">
            <FaSpinner className="animate-spin text-gray-800 h-12 w-12 mb-4" />
            <p className="text-gray-600">Loading...</p>
          </div>
        )}

        {currentQuestion && !isLoading && (
          <div className="mb-6">
            <div className="flex justify-between items-center mb-2">
              <span className="text-sm font-medium text-gray-500">
                Category: {currentQuestion.category}
              </span>
              <span className="text-sm font-medium text-gray-500">
                Difficulty: {currentQuestion.difficulty}
              </span>
            </div>            <div className="bg-gradient-to-r from-indigo-50 to-blue-50 p-5 rounded-lg mb-4 border border-indigo-100 shadow-sm">
              <h2 className="text-lg font-semibold text-gray-800 mb-2">
                Question {answeredQuestions + 1}
              </h2>
              <p className="text-gray-700">{currentQuestion.question_text}</p>
            </div>

            <div className="mb-4">
              <label
                htmlFor="answer"
                className="block text-sm font-medium text-gray-700 mb-1"
              >
                Your Answer
              </label>
              <textarea
                id="answer"
                rows={6}
                className="w-full px-3 py-2 border border-gray-300 rounded-md focus:outline-none focus:ring-2 focus:ring-gray-400"
                value={answer}
                onChange={(e) => setAnswer(e.target.value)}
                placeholder="Type your answer here..."
              ></textarea>
            </div>            <div className="flex justify-between">              <button
              onClick={submitAnswer}
              disabled={!answer.trim() || isLoading}
              className={`px-6 py-2 bg-indigo-600 text-white rounded-md hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-colors font-medium flex items-center justify-center ${!answer.trim() || isLoading ? 'opacity-50 cursor-not-allowed' : ''
                }`}
            >
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zm3.707-8.707l-3-3a1 1 0 00-1.414 0l-3 3a1 1 0 001.414 1.414L9 9.414V13a1 1 0 102 0V9.414l1.293 1.293a1 1 0 001.414-1.414z" clipRule="evenodd" />
              </svg>
              Submit Answer
            </button>

              {answeredQuestions > 0 && (<button
                onClick={finishInterview}
                className="px-6 py-2 border border-gray-300 text-white rounded-md hover:bg-gray-100 transition-colors font-medium flex items-center justify-center"
              >
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" viewBox="0 0 20 20" fill="currentColor">
                  <path fillRule="evenodd" d="M16.707 5.293a1 1 0 010 1.414l-8 8a1 1 0 01-1.414 0l-4-4a1 1 0 011.414-1.414L8 12.586l7.293-7.293a1 1 0 011.414 0z" clipRule="evenodd" />
                </svg>
                Finish Interview
              </button>
              )}
            </div>
          </div>
        )}        {evaluations.length > 0 && !interviewComplete && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h3 className="text-lg font-semibold text-gray-800 mb-3 flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2 text-indigo-500" viewBox="0 0 20 20" fill="currentColor">
                <path d="M10 12a2 2 0 100-4 2 2 0 000 4z" />
                <path fillRule="evenodd" d="M.458 10C1.732 5.943 5.522 3 10 3s8.268 2.943 9.542 7c-1.274 4.057-5.064 7-9.542 7S1.732 14.057.458 10zM14 10a4 4 0 11-8 0 4 4 0 018 0z" clipRule="evenodd" />
              </svg>
              Previous Answers
            </h3>
            <div className="space-y-3 max-h-64 overflow-y-auto custom-scrollbar pr-2">
              {evaluations.map((evaluation, index) => (
                <div
                  key={index}
                  className="p-4 bg-gray-50 rounded-md border border-gray-200 shadow-sm hover:shadow-md transition-shadow"
                >
                  <div className="flex justify-between items-center mb-2 pb-1 border-b border-gray-100">
                    <span className="text-indigo-700 font-medium">Question {index + 1}</span>
                  </div>
                  <p className="text-sm text-gray-700 mb-2"><span className="font-medium">Q:</span> {evaluation.question}</p>
                  <p className="text-sm text-gray-600 mb-2"><span className="font-medium">A:</span> {evaluation.answer}</p>
                  {evaluation.feedback && (
                    <div className="mt-2 pt-2 border-t border-gray-100">
                      <p className="text-sm text-gray-600"><span className="font-medium text-indigo-600">Feedback:</span> {evaluation.feedback}</p>
                    </div>
                  )}
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default InterviewInterface;
