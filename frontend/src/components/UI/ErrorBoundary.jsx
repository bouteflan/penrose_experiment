/**
 * Composant ErrorBoundary - Gestion des erreurs React
 * Capture les erreurs et affiche une interface de récupération
 */
import React from 'react';
import './ErrorBoundary.css';

class ErrorBoundary extends React.Component {
  constructor(props) {
    super(props);
    this.state = {
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null
    };
  }

  static getDerivedStateFromError(error) {
    // Met à jour le state pour afficher l'UI de fallback
    return {
      hasError: true,
      errorId: `error_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`
    };
  }

  componentDidCatch(error, errorInfo) {
    // Capture les détails de l'erreur
    this.setState({
      error,
      errorInfo
    });

    // Appeler le callback d'erreur si fourni
    if (this.props.onError) {
      this.props.onError(error, errorInfo);
    }

    // Log l'erreur
    console.error('🚨 ErrorBoundary caught an error:', error, errorInfo);
  }

  handleReset = () => {
    this.setState({
      hasError: false,
      error: null,
      errorInfo: null,
      errorId: null
    });
  };

  handleReload = () => {
    window.location.reload();
  };

  copyErrorToClipboard = () => {
    const { error, errorInfo, errorId } = this.state;
    
    const errorReport = `
REMOTE - Rapport d'erreur
========================
ID: ${errorId}
Date: ${new Date().toISOString()}
URL: ${window.location.href}
User Agent: ${navigator.userAgent}

Erreur:
${error?.toString() || 'Erreur inconnue'}

Stack:
${error?.stack || 'Pas de stack trace'}

Component Stack:
${errorInfo?.componentStack || 'Pas de component stack'}
    `.trim();

    navigator.clipboard.writeText(errorReport).then(() => {
      alert('Rapport d\'erreur copié dans le presse-papiers');
    }).catch(() => {
      console.error('Impossible de copier le rapport d\'erreur');
    });
  };

  render() {
    if (this.state.hasError) {
      const { error, errorInfo, errorId } = this.state;
      const isDevelopment = process.env.NODE_ENV === 'development';

      return (
        <div className="error-boundary">
          <div className="error-boundary-content">
            {/* Header */}
            <div className="error-header">
              <div className="error-icon">⚠️</div>
              <h1>Une erreur s'est produite</h1>
              <p className="error-subtitle">
                L'application a rencontré un problème inattendu
              </p>
            </div>

            {/* Message utilisateur */}
            <div className="error-message">
              <p>
                Nous nous excusons pour cet incident. L'erreur a été automatiquement 
                signalée à notre équipe.
              </p>
              
              {isDevelopment && (
                <div className="error-details">
                  <h3>Détails techniques (mode développement)</h3>
                  <div className="error-code">
                    <strong>ID:</strong> {errorId}
                  </div>
                  <div className="error-code">
                    <strong>Message:</strong> {error?.message || 'Erreur inconnue'}
                  </div>
                  {error?.stack && (
                    <details className="error-stack">
                      <summary>Stack trace</summary>
                      <pre>{error.stack}</pre>
                    </details>
                  )}
                  {errorInfo?.componentStack && (
                    <details className="error-component-stack">
                      <summary>Component stack</summary>
                      <pre>{errorInfo.componentStack}</pre>
                    </details>
                  )}
                </div>
              )}
            </div>

            {/* Actions */}
            <div className="error-actions">
              <button 
                className="error-button primary"
                onClick={this.handleReset}
              >
                Réessayer
              </button>
              
              <button 
                className="error-button secondary"
                onClick={this.handleReload}
              >
                Recharger la page
              </button>

              {isDevelopment && (
                <button 
                  className="error-button secondary"
                  onClick={this.copyErrorToClipboard}
                >
                  Copier le rapport
                </button>
              )}
            </div>

            {/* Suggestions */}
            <div className="error-suggestions">
              <h3>Que puis-je faire ?</h3>
              <ul>
                <li>Cliquer sur "Réessayer" pour continuer l'expérience</li>
                <li>Recharger la page si le problème persiste</li>
                <li>Vérifier votre connexion internet</li>
                <li>Fermer d'autres onglets pour libérer de la mémoire</li>
              </ul>
            </div>

            {/* Footer */}
            <div className="error-footer">
              <p>
                Si le problème persiste, contactez notre support en incluant 
                l'ID d'erreur : <code>{errorId}</code>
              </p>
            </div>
          </div>
        </div>
      );
    }

    return this.props.children;
  }
}

export default ErrorBoundary;
