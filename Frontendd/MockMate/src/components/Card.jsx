import React from 'react';

export const Card = ({ children, className }) => {
  return (
    <div className={`bg-white shadow-md rounded-lg p-4 ${className}`}>
      {children}
    </div>
  );
};

export const CardHeader = ({ children, className }) => {
  return (
    <div className={`border-b pb-2 mb-4 ${className}`}>
      {children}
    </div>
  );
};

export const CardTitle = ({ children, className }) => {
  return (
    <h2 className={`text-lg font-bold ${className}`}>{children}</h2>
  );
};

export const CardContent = ({ children, className }) => {
  return (
    <div className={`space-y-4 ${className}`}>
      {children}
    </div>
  );
};

export const CardDescription = ({ children, className }) => {
  return (
    <p className={`text-gray-600 ${className}`}>
      {children}
    </p>
  );
}
export const CardActions = ({ children, className }) => {
  return (
    <div className={`flex justify-end space-x-2 ${className}`}>
      {children}
    </div>
  );
};
