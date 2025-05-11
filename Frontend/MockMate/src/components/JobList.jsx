import React, { useState, useEffect } from 'react';
import axios from 'axios';

const JobList = () => {
  const [jobs, setJobs] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');
  const [selectedJob, setSelectedJob] = useState(null);

  useEffect(() => {
    fetchJobs();
  }, []);

  const fetchJobs = async () => {
    try {
      const response = await axios.get('http://localhost:8000/api/jobs/', {
        withCredentials: true
      });
      setJobs(response.data);
    } catch (err) {
      setError('Failed to fetch jobs');
    } finally {
      setLoading(false);
    }
  };

  const handleStartInterview = async (jobId) => {
    try {
      const response = await axios.post(
        'http://localhost:8000/api/start-interview/',
        { job_id: jobId },
        { withCredentials: true }
      );
      // Handle the interview start response
      console.log('Interview started:', response.data);
    } catch (err) {
      setError('Failed to start interview');
    }
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center h-64">
        <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="text-center p-8">
        <div className="text-xl text-red-600">{error}</div>
      </div>
    );
  }

  return (
    <div className="w-full">
      <div className="grid gap-8 md:grid-cols-2 lg:grid-cols-3">
        {jobs.map((job) => (
          <div
            key={job.id}
            className="bg-white rounded-xl shadow-xl overflow-hidden hover:shadow-2xl transition-all duration-300 transform hover:-translate-y-1"
          >
            <div className="p-8">
              <h3 className="text-2xl font-bold text-gray-900 mb-4">
                {job.title}
              </h3>
              <p className="text-xl text-gray-600 mb-6">{job.company}</p>
              <div className="mb-6">
                <span className="inline-block bg-gray-100 rounded-full px-4 py-2 text-lg font-semibold text-gray-700 mr-3">
                  {job.location}
                </span>
                <span className="inline-block bg-gray-100 rounded-full px-4 py-2 text-lg font-semibold text-gray-700">
                  {job.type}
                </span>
              </div>
              <p className="text-lg text-gray-700 mb-6 line-clamp-3">{job.description}</p>
              <div className="flex flex-wrap gap-3 mb-8">
                {job.skills.map((skill, index) => (
                  <span
                    key={index}
                    className="inline-block bg-indigo-100 text-indigo-800 rounded-full px-4 py-2 text-lg font-semibold"
                  >
                    {skill}
                  </span>
                ))}
              </div>
              <button
                onClick={() => handleStartInterview(job.id)}
                className="w-full bg-indigo-600 text-white px-8 py-4 rounded-lg text-lg font-medium hover:bg-indigo-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-indigo-500 transition-all duration-200"
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