import React from 'react';
import JobList from '../components/JobList';

const AllJobs = () => {
  return (
    <div className="container mx-auto py-16 px-6 sm:px-10 md:px-20">
      <div className="text-center mb-12">
        <h1 className="text-4xl font-bold text-gray-900">All Available Job Positions</h1>
        <p className="mt-2 text-lg text-gray-600">
          Browse through all job opportunities and find your perfect match for interview practice
        </p>
      </div>
      <JobList />
    </div>
  );
};

export default AllJobs;
