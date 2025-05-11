import React, { useState, useEffect } from 'react';
import Navbar from '../components/Navbar';
import CVUpload from '../components/CVUpload';
import JobList from '../components/JobList';

const Home = () => {
  const [hasCV, setHasCV] = useState(false);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    checkCVStatus();
  }, []);

  const checkCVStatus = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/cv-status/', {
        credentials: 'include'
      });
      
      if (!response.ok) {
        throw new Error('Failed to check CV status');
      }

      const data = await response.json();
      setHasCV(data.has_cv);
    } catch (err) {
      console.error('Error checking CV status:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleCVUploadSuccess = () => {
    setHasCV(true);
  };

  if (loading) {
    return (
      <div className="flex justify-center items-center min-h-screen">
        <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-indigo-600"></div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navbar />
      <main>
        {!hasCV ? (
          <div className="py-12">
            <CVUpload onUploadSuccess={handleCVUploadSuccess} />
          </div>
        ) : (
          <JobList />
        )}
      </main>
    </div>
  );
};

export default Home; 