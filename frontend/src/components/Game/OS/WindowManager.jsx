/**
 * Composant WindowManager - Gère l'affichage et les interactions des fenêtres
 * Simule un gestionnaire de fenêtres Windows-like
 */
import React, { useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useOSStore } from '../../../stores/osStore';
import FilePropertiesWindow from './FilePropertiesWindow';
import './WindowManager.css';

const WindowManager = ({ 
  windows, 
  onPlayerAction, 
  corruptionLevel 
}) => {
  // Store OS
  const osStore = useOSStore();

  /**
   * Gestionnaire de fermeture de fenêtre
   */
  const handleCloseWindow = useCallback((windowId) => {
    osStore.closeWindow(windowId);
    
    onPlayerAction({
      type: 'window_closed',
      window_id: windowId,
      is_meta_action: true
    });
  }, [osStore, onPlayerAction]);

  /**
   * Gestionnaire de focus de fenêtre
   */
  const handleFocusWindow = useCallback((windowId) => {
    osStore.focusWindow(windowId);
    
    onPlayerAction({
      type: 'window_focused',
      window_id: windowId,
      is_meta_action: true
    });
  }, [osStore, onPlayerAction]);

  /**
   * Gestionnaire de redimensionnement
   */
  const handleResizeWindow = useCallback((windowId, newSize) => {
    osStore.updateWindow(windowId, { size: newSize });
    
    onPlayerAction({
      type: 'window_resized',
      window_id: windowId,
      new_size: newSize,
      is_meta_action: true
    });
  }, [osStore, onPlayerAction]);

  /**
   * Gestionnaire de déplacement
   */
  const handleMoveWindow = useCallback((windowId, newPosition) => {
    osStore.updateWindow(windowId, { position: newPosition });
    
    onPlayerAction({
      type: 'window_moved',
      window_id: windowId,
      new_position: newPosition,
      is_meta_action: true
    });
  }, [osStore, onPlayerAction]);

  /**
   * Rendu d'une fenêtre selon son type
   */
  const renderWindow = useCallback((window) => {
    switch (window.type) {
      case 'file_properties':
        return (
          <FilePropertiesWindow
            window={window}
            onClose={() => handleCloseWindow(window.id)}
            onFocus={() => handleFocusWindow(window.id)}
            onPlayerAction={onPlayerAction}
            corruptionLevel={corruptionLevel}
          />
        );
      
      case 'folder_view':
        return (
          <FolderViewWindow
            window={window}
            onClose={() => handleCloseWindow(window.id)}
            onFocus={() => handleFocusWindow(window.id)}
            onPlayerAction={onPlayerAction}
            corruptionLevel={corruptionLevel}
          />
        );
      
      case 'system_info':
        return (
          <SystemInfoWindow
            window={window}
            onClose={() => handleCloseWindow(window.id)}
            onFocus={() => handleFocusWindow(window.id)}
            onPlayerAction={onPlayerAction}
            corruptionLevel={corruptionLevel}
          />
        );
      
      default:
        return (
          <GenericWindow
            window={window}
            onClose={() => handleCloseWindow(window.id)}
            onFocus={() => handleFocusWindow(window.id)}
            onPlayerAction={onPlayerAction}
            corruptionLevel={corruptionLevel}
          />
        );
    }
  }, [handleCloseWindow, handleFocusWindow, onPlayerAction, corruptionLevel]);

  /**
   * Tri des fenêtres par z-index
   */
  const sortedWindows = windows.sort((a, b) => (a.zIndex || 0) - (b.zIndex || 0));

  return (
    <div className="window-manager">
      <AnimatePresence>
        {sortedWindows.map((window) => (
          <motion.div
            key={window.id}
            className={`window-container ${window.type}`}
            style={{ zIndex: window.zIndex || 100 }}
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            exit={{ opacity: 0, scale: 0.9 }}
            transition={{ duration: 0.2 }}
          >
            {renderWindow(window)}
          </motion.div>
        ))}
      </AnimatePresence>
    </div>
  );
};

/**
 * Composant générique de fenêtre
 */
const GenericWindow = ({ 
  window, 
  onClose, 
  onFocus, 
  onPlayerAction, 
  corruptionLevel 
}) => {
  return (
    <motion.div
      className="generic-window"
      style={{
        position: 'absolute',
        left: window.position?.x || 100,
        top: window.position?.y || 100,
        width: window.size?.width || 400,
        height: window.size?.height || 300
      }}
      drag
      dragMomentum={false}
      onClick={onFocus}
    >
      {/* Header de la fenêtre */}
      <div className="window-header">
        <div className="window-title">
          <span className="window-icon">🖼️</span>
          <span>{window.title || 'Fenêtre'}</span>
        </div>
        <div className="window-controls">
          <button className="window-control minimize">−</button>
          <button className="window-control maximize">□</button>
          <button 
            className="window-control close"
            onClick={onClose}
          >
            ×
          </button>
        </div>
      </div>

      {/* Contenu de la fenêtre */}
      <div className="window-content">
        <p>Contenu de la fenêtre : {window.type}</p>
        {window.content && (
          <pre>{JSON.stringify(window.content, null, 2)}</pre>
        )}
      </div>
    </motion.div>
  );
};

export default WindowManager;
