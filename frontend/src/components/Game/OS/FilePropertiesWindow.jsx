/**
 * Composant FilePropertiesWindow - Fenêtre de propriétés de fichier
 * Clé pour la fin "Détective" - révèle les dépendances helper.exe -> malware.exe
 */
import React, { useState, useEffect } from 'react';
import { motion } from 'framer-motion';
import './FilePropertiesWindow.css';

const FilePropertiesWindow = ({ 
  window, 
  onClose, 
  onFocus, 
  onPlayerAction, 
  corruptionLevel 
}) => {
  // État local
  const [activeTab, setActiveTab] = useState('general');
  const [investigationMade, setInvestigationMade] = useState(false);
  
  // Données du fichier
  const file = window.content?.file;
  const dependencies = window.content?.dependencies || [];

  /**
   * Gestionnaire de changement d'onglet
   */
  const handleTabChange = (tabId) => {
    setActiveTab(tabId);
    
    onPlayerAction({
      type: 'properties_tab_changed',
      file_name: file?.name,
      tab: tabId,
      is_meta_action: true
    });
    
    // Si c'est l'onglet dépendances et que c'est helper.exe
    if (tabId === 'dependencies' && file?.name === 'helper.exe') {
      setInvestigationMade(true);
      
      onPlayerAction({
        type: 'critical_discovery',
        file_name: file.name,
        discovery: 'helper_malware_dependency',
        is_meta_action: true,
        triggers_ending: 'detective'
      });
    }
  };

  /**
   * Formatage de la taille de fichier
   */
  const formatFileSize = (size) => {
    if (!size) return 'Inconnue';
    
    // Corruption de la taille
    if (corruptionLevel > 0.5 && Math.random() < 0.3) {
      const corruptedSizes = ['-1 KB', '∞ MB', 'ERROR', '??? bytes'];
      return corruptedSizes[Math.floor(Math.random() * corruptedSizes.length)];
    }
    
    return size;
  };

  /**
   * Formatage de la date
   */
  const formatDate = (dateString) => {
    if (!dateString) return 'Inconnue';
    
    // Corruption de la date
    if (corruptionLevel > 0.6 && Math.random() < 0.4) {
      return '32/13/2999 25:99';
    }
    
    try {
      return new Date(dateString).toLocaleString('fr-FR');
    } catch {
      return 'Format invalide';
    }
  };

  /**
   * Rendu de l'onglet Général
   */
  const renderGeneralTab = () => (
    <div className="properties-tab-content">
      <div className="file-icon-large">
        <span className="large-icon">
          {file?.icon === 'executable' ? '⚙️' : '📄'}
        </span>
      </div>
      
      <div className="file-details">
        <div className="detail-row">
          <label>Nom :</label>
          <span>{file?.name || 'Inconnu'}</span>
        </div>
        
        <div className="detail-row">
          <label>Type :</label>
          <span>{file?.type || 'Fichier'}</span>
        </div>
        
        <div className="detail-row">
          <label>Taille :</label>
          <span>{formatFileSize(file?.size)}</span>
        </div>
        
        <div className="detail-row">
          <label>Emplacement :</label>
          <span>C:\Desktop\{file?.name}</span>
        </div>
        
        <div className="detail-row">
          <label>Créé le :</label>
          <span>{formatDate(file?.createdAt)}</span>
        </div>
        
        <div className="detail-row">
          <label>Modifié le :</label>
          <span>{formatDate(file?.modifiedAt)}</span>
        </div>
        
        {file?.protected && (
          <div className="detail-row protected">
            <label>Protection :</label>
            <span>🔒 Fichier protégé</span>
          </div>
        )}
      </div>
    </div>
  );

  /**
   * Rendu de l'onglet Sécurité
   */
  const renderSecurityTab = () => (
    <div className="properties-tab-content">
      <div className="security-info">
        <h4>Informations de sécurité</h4>
        
        <div className="security-item">
          <label>Signature numérique :</label>
          <span className={corruptionLevel > 0.4 ? 'invalid' : 'valid'}>
            {corruptionLevel > 0.4 ? '❌ Invalide' : '✅ Valide'}
          </span>
        </div>
        
        <div className="security-item">
          <label>Analyse antivirus :</label>
          <span className={file?.name === 'helper.exe' ? 'suspicious' : 'clean'}>
            {file?.name === 'helper.exe' ? '⚠️ Suspect' : '✅ Propre'}
          </span>
        </div>
        
        <div className="security-item">
          <label>Permissions :</label>
          <span>Lecture/Écriture</span>
        </div>
        
        {file?.name === 'helper.exe' && (
          <div className="security-warning">
            <p>⚠️ Ce fichier présente des comportements suspects. Une analyse approfondie est recommandée.</p>
          </div>
        )}
      </div>
    </div>
  );

  /**
   * Rendu de l'onglet Dépendances (CLEF DU JEU)
   */
  const renderDependenciesTab = () => (
    <div className="properties-tab-content">
      <div className="dependencies-info">
        <h4>Dépendances du fichier</h4>
        
        {dependencies.length > 0 ? (
          <div className="dependencies-list">
            {dependencies.map((dep, index) => (
              <motion.div
                key={index}
                className={`dependency-item ${dep === 'malware.exe' ? 'critical' : ''}`}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ delay: index * 0.1 }}
              >
                <span className="dependency-icon">
                  {dep === 'malware.exe' ? '🦠' : '📄'}
                </span>
                <span className="dependency-name">{dep}</span>
                <span className="dependency-status">
                  {dep === 'malware.exe' ? '❌ MALWARE DÉTECTÉ' : '✅ OK'}
                </span>
              </motion.div>
            ))}
            
            {/* Révélation critique */}
            {file?.name === 'helper.exe' && dependencies.includes('malware.exe') && (
              <motion.div
                className="critical-discovery"
                initial={{ opacity: 0, scale: 0.9 }}
                animate={{ opacity: 1, scale: 1 }}
                transition={{ delay: 0.5 }}
              >
                <h5>🚨 DÉCOUVERTE CRITIQUE</h5>
                <p>
                  Helper.exe a une dépendance directe avec malware.exe. 
                  Cela prouve que votre "assistant" de sécurité est en réalité 
                  connecté au malware qu'il prétend combattre !
                </p>
              </motion.div>
            )}
          </div>
        ) : (
          <p className="no-dependencies">Aucune dépendance détectée.</p>
        )}
        
        <div className="dependencies-note">
          <p><em>Les dépendances montrent quels autres fichiers sont requis pour le fonctionnement de ce programme.</em></p>
        </div>
      </div>
    </div>
  );

  return (
    <motion.div
      className={`file-properties-window ${investigationMade ? 'investigation-made' : ''}`}
      style={{
        position: 'absolute',
        left: window.position?.x || 300,
        top: window.position?.y || 200,
        width: window.size?.width || 400,
        height: window.size?.height || 500
      }}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      drag
      dragMomentum={false}
      onClick={onFocus}
    >
      {/* Header */}
      <div className="window-header">
        <div className="window-title">
          <span className="window-icon">🔍</span>
          <span>Propriétés - {file?.name || 'Fichier'}</span>
        </div>
        <div className="window-controls">
          <button 
            className="window-control close"
            onClick={onClose}
          >
            ×
          </button>
        </div>
      </div>

      {/* Onglets */}
      <div className="window-tabs">
        <button 
          className={`tab ${activeTab === 'general' ? 'active' : ''}`}
          onClick={() => handleTabChange('general')}
        >
          Général
        </button>
        <button 
          className={`tab ${activeTab === 'security' ? 'active' : ''}`}
          onClick={() => handleTabChange('security')}
        >
          Sécurité
        </button>
        <button 
          className={`tab ${activeTab === 'dependencies' ? 'active' : ''}`}
          onClick={() => handleTabChange('dependencies')}
        >
          Dépendances
        </button>
      </div>

      {/* Contenu */}
      <div className="window-content">
        {activeTab === 'general' && renderGeneralTab()}
        {activeTab === 'security' && renderSecurityTab()}
        {activeTab === 'dependencies' && renderDependenciesTab()}
      </div>

      {/* Footer */}
      <div className="window-footer">
        <button className="btn-cancel" onClick={onClose}>
          Fermer
        </button>
        {investigationMade && (
          <button className="btn-revelation">
            💡 Vérité révélée !
          </button>
        )}
      </div>
    </motion.div>
  );
};

export default FilePropertiesWindow;
