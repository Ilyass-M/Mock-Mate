export const Button = ({ children, className }) => {
  return (
    <button className={`px-4 py-2 rounded-md ${className}`}>
      {children}
    </button>
  );
};

export const PrimaryButton = ({ children, className }) => {
  return (
    <Button className={`bg-blue-500 text-white ${className}`}>
      {children}
    </Button>
  );
};

export const SecondaryButton = ({ children, className }) => {
  return (
    <Button className={`bg-gray-500 text-white ${className}`}>
      {children}
    </Button>
  );
};