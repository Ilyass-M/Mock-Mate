import React, { useState, useEffect, useRef, useCallback } from 'react';
import { useAuth } from '../context/AuthContext';
import { useNavigate, useLocation } from 'react-router-dom';
import { toast } from 'sonner';
import { MessageSquare, Send, Loader2, ArrowLeft } from 'lucide-react';
import Cookies from 'universal-cookie';
const Interview = () => {
  const { user } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [messages, setMessages] = useState([]);
  const [inputMessage, setInputMessage] = useState('');
  const [isConnected, setIsConnected] = useState(false);
  const [isLoading, setIsLoading] = useState(false);
  const [interviewId, setInterviewId] = useState(null);
  const [jobDetails, setJobDetails] = useState(null);
  const cookies = new Cookies();
  const ws = useRef(null);
  const messagesEndRef = useRef(null);
  const getCookie = (name) => {
    const value = `; ${document.cookie}`;
    const parts = value.split(`; ${name}=`);
    if (parts.length === 2) return parts.pop().split(';').shift();
  };  useEffect(() => {
    const params = new URLSearchParams(location.search);
    const sessionId = params.get('session');
    const jobId = params.get('job');

    if (!sessionId || !jobId) {
      toast.error('Invalid interview session');
      navigate('/jobs');
      return;
    }

    setInterviewId(jobId);
    // Connect directly to the WebSocket without fetching job details
    connectWebSocket(jobId);
    
    // Cleanup function to close WebSocket when component unmounts
    return () => {
      if (ws.current) {
        ws.current.close();
      }
    };
  }, [location.search, navigate, connectWebSocket]);

  const fetchJobDetails = async (jobId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/JobDescription/${jobId}/`, {
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error('Failed to fetch job details');
      }

      const data = await response.json();
      console.log("Job Details:", data);
      setJobDetails(data);
      connectWebSocket(interviewId);
    } catch (error) {
      toast.error(error.message);
      navigate('/jobs');
    }
  };

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  useEffect(() => {
    scrollToBottom();
  }, [messages]);
  const connectWebSocket = useCallback((id) => {
    if (!id) {
      console.error("Interview ID is missing");
      return;
    }

    // Use the hardcoded token for now
    const token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ0b2tlbl90eXBlIjoiYWNjZXNzIiwiZXhwIjoxNzQ3NjQ3Mzk2LCJpYXQiOjE3NDcwNDI1OTYsImp0aSI6IjgzZDRmNDRhNmY3NzQ5NGViOWMzOGU2ZTJmYTc3ZjIyIiwidXNlcl9pZCI6MX0.jcPUcqdPJKY50S-5E59a2oZ4epw4JrzeDguyKjI9DP4";
    console.log("Using token:", token);
    const wsUrl = `ws://127.0.0.1:8000/interview/${id}/?token=${token}`;
    ws.current = new WebSocket(wsUrl);

    ws.current.onopen = () => {
      setIsConnected(true);
      ws.current.send(
        JSON.stringify({
          type: "start_interview",
          message: "",
        })
      );
    };

    ws.current.onmessage = (event) => {
      const data = JSON.parse(event.data);
      setMessages((prev) => [
        ...prev,
        {
          type: data.type,
          content: data.message,
          sender: data.type === "question" ? "ai" : "user",
        },
      ]);
    };

    ws.current.onclose = (event) => {
      setIsConnected(false);
      console.warn("WebSocket closed", event);
      if (!event.wasClean) {
        toast.error("WebSocket connection lost. Reconnecting...");
        setTimeout(() => connectWebSocket(id), 5000); // Reconnect after 5 seconds
      }
    };

    ws.current.onerror = (error) => {
      console.error("WebSocket error:", error);
      toast.error("Connection error. Please try again.");
    };
  };

  const sendMessage = () => {
    if (!inputMessage.trim() || !isConnected) return;

    const message = {
      type: 'answer',
      message: inputMessage
    };

    ws.current.send(JSON.stringify(message));
    setMessages(prev => [...prev, {
      type: 'answer',
      content: inputMessage,
      sender: 'user'
    }]);
    setInputMessage('');
  };

  const endInterview = async () => {
    if (!interviewId) return;

    try {
      const response = await fetch(`http://localhost:8000/api/interview-sessions/${interviewId}/end/`, {
        method: 'POST',
        credentials: 'include',
      });

      if (!response.ok) {
        throw new Error('Failed to end interview');
      }

      ws.current.send(JSON.stringify({
        type: 'end_interview',
        message: ''
      }));

      ws.current.close();
    } catch (error) {
      toast.error(error.message);
    }
  };

  const handleBack = () => {
    if (messages.length > 0) {
      if (window.confirm('Are you sure you want to leave? Your progress will be lost.')) {
        navigate('/jobs');
      }
    } else {
      navigate('/jobs');
    }
  };

  return (
    <div className="max-w-4xl mx-auto p-6">
      <div className="bg-white rounded-lg shadow-xl overflow-hidden">
        <div className="p-6 border-b border-gray-200">
          <div className="flex items-center justify-between">
            <button
              onClick={handleBack}
              className="flex items-center text-gray-600 hover:text-gray-900"
            >
              <ArrowLeft className="w-5 h-5 mr-2" />
              Back to Jobs
            </button>
            <div className="text-right">
              <h2 className="text-2xl font-bold text-gray-900">AI Interview Session</h2>
              {jobDetails && (
                <p className="mt-1 text-sm text-gray-600">
                  {jobDetails.title} at {jobDetails.company_name}
                </p>
              )}
            </div>
          </div>
        </div>

        <div className="flex flex-col h-[600px]">
          <div className="flex-1 overflow-y-auto p-6 space-y-4">
            {messages.map((message, index) => (
              <div
                key={index}
                className={`flex ${message.sender === 'user' ? 'justify-end' : 'justify-start'}`}
              >
                <div
                  className={`max-w-[70%] rounded-lg px-4 py-2 ${message.sender === 'user'
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-100 text-gray-900'
                    }`}
                >
                  {message.type === 'evaluation' && (
                    <div className="text-sm font-medium mb-1">Evaluation:</div>
                  )}
                  {message.type === 'final_decision' && (
                    <div className="text-sm font-medium mb-1">Final Decision:</div>
                  )}
                  <p className="text-sm">{message.content}</p>
                </div>
              </div>
            ))}
            <div ref={messagesEndRef} />
          </div>

          <div className="border-t border-gray-200 p-4">
            <div className="flex space-x-4">
              <input
                type="text"
                value={inputMessage}
                onChange={(e) => setInputMessage(e.target.value)}
                onKeyPress={(e) => e.key === 'Enter' && sendMessage()}
                placeholder="Type your answer..."
                className="flex-1 rounded-lg border-gray-300 focus:ring-indigo-500 focus:border-indigo-500"
                disabled={!isConnected}
              />
              <button
                onClick={sendMessage}
                disabled={!isConnected || !inputMessage.trim()}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <Send className="h-5 w-5" />
              </button>
              <button
                onClick={endInterview}
                className="inline-flex items-center px-4 py-2 border border-transparent text-sm font-medium rounded-md shadow-sm text-white bg-red-600 hover:bg-red-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-red-500"
              >
                End Interview
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Interview;