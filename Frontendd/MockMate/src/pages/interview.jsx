import { useState, useEffect, useRef } from 'react';
import { useParams } from 'react-router-dom';
import { useAuth } from '../context/AuthContext';

const InterviewInterface = () => {
  const { id } = useParams();
  const { user } = useAuth();
  const [socket, setSocket] = useState(null);
  const [connected, setConnected] = useState(false);
  const [currentQuestion, setCurrentQuestion] = useState(null);
  const [answer, setAnswer] = useState('');
  const [evaluations, setEvaluations] = useState([]);
  const [result, setResult] = useState(null);
  const [error, setError] = useState(null);
  const [isLoading, setIsLoading] = useState(false);
  const [answeredQuestions, setAnsweredQuestions] = useState(0);
  const [interviewComplete, setInterviewComplete] = useState(false);

  const socketRef = useRef(null);

  useEffect(() => {
    // const wsProtocol = window.location.protocol ===  'ws:';
    const wsUrl = `ws://127.0.0.1:8000/interview/${id}/?token=${user?.accessToken}`;

    const ws = new WebSocket(wsUrl);
    socketRef.current = ws;
    setSocket(ws);

    ws.onopen = () => {
      console.log('WebSocket connected');
      setConnected(true);
      setError(null);
    };

    ws.onmessage = (event) => {
      const data = JSON.parse(event.data);
      console.log('Received message:', data);

      if (data.type === 'question') {
        setCurrentQuestion(data.question);
        setAnswer('');
        setIsLoading(false);
      } else if (data.type === 'answer_evaluation') {
        setEvaluations((prev) => [...prev, data]);
        setAnsweredQuestions((prev) => prev + 1);
        setIsLoading(false);
        requestNextQuestion();
      } else if (data.type === 'interview_result') {
        setResult(data);
        setInterviewComplete(true);
        setIsLoading(false);
      } else if (data.type === 'error') {
        setError(data.message);
        setIsLoading(false);
      }
    };

    ws.onerror = (error) => {
      console.error('WebSocket error:', error);
      setError('Connection error. Please try again.');
      setConnected(false);
    };

    ws.onclose = () => {
      console.log('WebSocket disconnected');
      setConnected(false);
    };

    return () => {
      if (socketRef.current) {
        socketRef.current.close();
      }
    };
  }, [id]);

  const requestNextQuestion = () => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      setIsLoading(true);
      socketRef.current.send(
        JSON.stringify({
          type: 'get_question',
        })
      );
    }
  };

  const submitAnswer = () => {
    if (!currentQuestion || !answer.trim()) return;

    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      setIsLoading(true);
      socketRef.current.send(
        JSON.stringify({
          type: 'submit_answer',
          question_id: currentQuestion.id,
          answer: answer.trim(),
        })
      );
    }
  };

  const finishInterview = () => {
    if (socketRef.current && socketRef.current.readyState === WebSocket.OPEN) {
      setIsLoading(true);
      socketRef.current.send(
        JSON.stringify({
          type: 'finish_interview',
        })
      );
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
          <p className="text-gray-600 mb-4">Connecting to interview session...</p>
          {error && (
            <div className="bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded mb-4">
              {error}
            </div>
          )}
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
          </div>

          <div className="mb-6">
            <h2 className="text-xl font-semibold mb-2">Performance Summary</h2>
            <p className="text-gray-700">
              You answered {answeredQuestions} questions in this interview.
            </p>
            <div className="mt-4">
              <h3 className="font-medium mb-2">Answer Evaluations:</h3>
              {evaluations.length > 0 ? (
                <ul className="space-y-2">
                  {evaluations.map((evaluation, index) => (
                    <li
                      key={index}
                      className="flex justify-between items-center border-b pb-2"
                    >
                      <span>Question {index + 1}</span>
                      <span className={getScoreColor(evaluation.similarity_score)}>
                        Score: {Math.round(evaluation.similarity_score * 100)}%
                      </span>
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
              onClick={() => (window.location.href = '/dashboard')}
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
          </div>
        )}

        {!currentQuestion && !isLoading && (
          <div className="text-center py-8">
            <h2 className="text-xl font-semibold mb-4">Ready to start your interview?</h2>
            <p className="text-gray-600 mb-6">
              You'll be asked a series of questions related to the job description and your
              skills. Answer each question thoroughly to get the best evaluation.
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
            <div className="animate-spin rounded-full h-12 w-12 border-t-2 border-b-2 border-gray-900 mb-4"></div>
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
                  className="flex justify-between items-center p-3 bg-gray-50 rounded-md"
                >
                  <span className="text-gray-700">Question {index + 1}</span>
                  <span className={getScoreColor(evaluation.similarity_score)}>
                    Score: {Math.round(evaluation.similarity_score * 100)}%
                  </span>
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
