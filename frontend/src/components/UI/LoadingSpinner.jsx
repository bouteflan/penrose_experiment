/**
 * Composant LoadingSpinner - Affichage de chargement élégant
 */
import React from 'react';
import './LoadingSpinner.css';

const LoadingSpinner = ({ 
  message = 'Chargement...', 
  size = 'medium',
  variant = 'dots' // 'dots', 'circle', 'bars'
}) => {
  
  const renderSpinner = () => {
    switch (variant) {
      case 'circle':
        return (
          <div className={`spinner-circle spinner-${size}`}>
            <div className="circle-inner"></div>
          </div>
        );
      
      case 'bars':
        return (
          <div className={`spinner-bars spinner-${size}`}>
            <div className="bar"></div>
            <div className="bar"></div>
            <div className="bar"></div>
            <div className="bar"></div>
          </div>
        );
      
      case 'dots':
      default:
        return (
          <div className={`spinner-dots spinner-${size}`}>
            <div className="dot"></div>
            <div className="dot"></div>
            <div className="dot"></div>
          </div>
        );
    }
  };

  return (
    <div className="loading-spinner-container">
      <div className="loading-spinner">
        {renderSpinner()}
        {message && (
          <div className="loading-message">
            {message}
          </div>
        )}
      </div>
    </div>
  );
};

export default LoadingSpinner;
