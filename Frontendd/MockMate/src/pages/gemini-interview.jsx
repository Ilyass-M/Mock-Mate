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
      });      if (!response.ok) {
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
      });      if (!response.ok) {
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
  };
  const finishInterview = async () => {
    try {
      setIsLoading(true);
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
  };

  const startInterview = () => {
    requestNextQuestion();
  };

  const getScoreColor = (score) => {
    if (score >= 0.8) return 'text-green-600';
    if (score >= 0.6) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (!connected) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
        <div className="w-full max-w-2xl bg-white rounded-lg shadow-md p-6">
          <h1 className="text-2xl font-bold text-gray-800 mb-4">Interview System</h1>
          <p className="text-gray-600 mb-4">Unable to connect to interview session.</p>
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}
          <button
            onClick={() => navigate('/')}
            className="px-4 py-2 bg-gray-800 text-white rounded-md hover:bg-gray-700"
          >
            Return to Dashboard
          </button>
        </div>
      </div>
    );
  }

  if (interviewComplete && result) {
    return (
      <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
        <div className="w-full max-w-2xl bg-white rounded-lg shadow-md p-6">
          <h1 className="text-2xl font-bold text-gray-800 mb-4">Interview Complete</h1>

          <div className="mb-6 p-4 rounded-lg bg-gray-100">
            <h2 className="text-xl font-semibold mb-2">Results</h2>
            <p className="text-lg mb-2">
              Decision:{' '}
              <span
                className={
                  result.decision === 'Hire'
                    ? 'text-green-600 font-bold'
                    : 'text-red-600 font-bold'
                }
              >
                {result.decision}
              </span>
            </p>
            <p className="text-lg mb-2">
              Confidence: {Math.round(result.probability[1] * 100)}%
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
          </div>

          <div className="flex justify-center">
            <button
              onClick={() => navigate('/dashboard')}
              className="px-6 py-2 bg-gray-800 text-white rounded-md hover:bg-gray-700 transition-colors"
            >
              Return to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-2xl bg-white rounded-lg shadow-md p-6">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-2xl font-bold text-gray-800">AI Interview</h1>
          <div className="text-sm text-gray-600">{user?.email}</div>
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
        )}

        {!currentQuestion && !isLoading && (
          <div className="text-center py-8">
            <h2 className="text-xl font-semibold mb-4">Ready to start your AI-powered interview?</h2>
            <p className="text-gray-600 mb-6">
              You'll be asked a series of questions generated by AI, tailored to the job description.
              Each answer will be evaluated by the AI with detailed feedback.
            </p>
            <button
              onClick={startInterview}
              className="px-6 py-3 bg-gray-800 text-white rounded-md hover:bg-gray-700 transition-colors"
            >
              Start Interview
            </button>
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
            </div>

            <div className="bg-gray-100 p-4 rounded-lg mb-4">
              <h2 className="text-lg font-medium text-gray-800 mb-1">
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
            </div>

            <div className="flex justify-between">
              <button
                onClick={submitAnswer}
                disabled={!answer.trim() || isLoading}
                className={`px-4 py-2 bg-gray-800 text-white rounded-md hover:bg-gray-700 transition-colors ${
                  !answer.trim() || isLoading ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                Submit Answer
              </button>

              {answeredQuestions > 0 && (
                <button
                  onClick={finishInterview}
                  className="px-4 py-2 border border-gray-300 text-gray-700 rounded-md hover:bg-gray-100 transition-colors"
                >
                  Finish Interview
                </button>
              )}
            </div>
          </div>
        )}

        {evaluations.length > 0 && !interviewComplete && (
          <div className="mt-6 pt-6 border-t border-gray-200">
            <h3 className="text-lg font-medium text-gray-800 mb-3">Previous Answers</h3>
            <div className="space-y-3">
              {evaluations.map((evaluation, index) => (
                <div
                  key={index}
                  className="p-3 bg-gray-50 rounded-md"
                >
                  <div className="flex justify-between items-center mb-2">
                    <span className="text-gray-700 font-medium">Question {index + 1}</span>
                    
                  </div>
                  <p className="text-sm text-gray-600 mb-1"><span className="font-medium">Q:</span> {evaluation.question}</p>
                  {evaluation.feedback && (
                    <p className="text-sm italic text-gray-500 mt-1">{evaluation.feedback}</p>
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
