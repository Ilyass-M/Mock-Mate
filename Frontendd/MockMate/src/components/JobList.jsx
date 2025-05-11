import axios from 'axios';
import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';

const JobList = () => {
  const navigate = useNavigate();
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/JobDescription/', {withCredentials: true});
      if (!response) {
        console.error(response);
        throw new Error('Failed to fetch jobs');
      }
      console.log(response.data);
      setJobs([...response.data]);
    } catch (err) {
      setError('Failed to load jobs. Please try again later.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const startInterview = async (jobId) => {
    try {
      const response = await fetch(`http://localhost:8000/api/start-interview/${jobId}/`, {
        method: 'POST',
        credentials: 'include'
      });

      if (!response.ok) {
        throw new Error('Failed to start interview');
      }

      const data = await response.json();
      navigate(`/interview/${data.interview_id}`);
    } catch (err) {
      setError('Failed to start interview. Please try again.');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
        <div className="bg-red-50 p-4 rounded-lg">
          <p className="text-red-700">{error}</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-12">
      <div className="text-center mb-12">
        {/* <h2 className="text-3xl font-bold text-gray-900">Available Jobs</h2>
        <p className="mt-2 text-sm text-gray-600">
          Select a job to start your AI-powered interview preparation
        </p> */}
      </div>

      <div className="grid grid-cols-1 gap-6 sm:grid-cols-2 lg:grid-cols-3">
        {jobs.map((job) => (
          <div
            key={job.id}
            className="bg-white overflow-hidden divide-y divide-gray-200 border-2 border-gray-200 rounded-2xl shadow-lg hover:shadow-xl transition-all duration-300"
          >
            <div className="px-4 py-5 sm:px-6">
              <h3 className="text-lg font-medium text-gray-900">{job.title}</h3>
              {/* <p className="mt-1 text-sm text-gray-500">{job?.company}</p> */}
            </div>
            <div className="px-4 py-5 sm:p-6">
              <div className="space-y-4">
                <div>
                  <h4 className="text-sm font-medium text-gray-900">Requirements</h4>
                  <ul className="mt-1 text-sm text-gray-500 list-disc list-inside">
                    {job.skills.map((req, index) => (
                      <li key={index}>{req.name}</li>
                    ))}
                  </ul>
                </div>
                <div>
                  <h4 className="text-sm font-medium text-gray-900">Description</h4>
                  <p className="mt-1 text-sm text-gray-500 line-clamp-3">
                    {job.description.replace(/\\r\\n/g, ' ')} {/* Replace \r\n with a space */}
                  </p>
                </div>
              </div>
            </div>
            <div className="px-4 py-4 sm:px-6">
              <button
                onClick={() => startInterview(job.id)}
                className="w-full flex justify-center py-2 px-4 border border-transparent rounded-md shadow-sm text-sm font-medium text-white bg-indigo-600 hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500"
              >
                Start Interview
              </button>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default JobList; 