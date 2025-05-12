import React from "react";
import PropTypes from "prop-types";
import classNames from "classnames";

export const Avatar = ({ className, children }) => {
  return (
    <div
      className={classNames(
        "relative flex items-center justify-center rounded-full overflow-hidden bg-gray-200",
        className
      )}
    >
      {children}
    </div>
  );
};

Avatar.propTypes = {
  className: PropTypes.string,
  children: PropTypes.node,
};

export const AvatarImage = ({ src, alt, className }) => {
  return (
    <img
      src={src}
      alt={alt}
      className={classNames("object-cover w-full h-full", className)}
    />
  );
};

AvatarImage.propTypes = {
  src: PropTypes.string.isRequired,
  alt: PropTypes.string,
  className: PropTypes.string,
};

export const AvatarFallback = ({ children, className }) => {
  return (
    <div
      className={classNames(
        "flex items-center justify-center w-full h-full text-gray-500",
        className
      )}
    >
      {children}
    </div>
  );
};

AvatarFallback.propTypes = {
  children: PropTypes.node.isRequired,
  className: PropTypes.string,
};
