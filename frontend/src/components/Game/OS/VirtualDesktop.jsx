/**
 * Composant VirtualDesktop - Simulation du bureau virtuel
 * Affiche le fond d'écran, les fichiers, widgets et fenêtres
 */
import React, { useEffect, useRef, useState, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';

// Stores
import { useOSStore } from '../../../stores/osStore';
import { useGameStore } from '../../../stores/gameStore';

// Composants
import DesktopFile from './DesktopFile';
import DesktopFolder from './DesktopFolder';
import DesktopWidget from './DesktopWidget';
import WindowManager from './WindowManager';
import ContextMenu from './ContextMenu';

// Styles
import './VirtualDesktop.css';

const VirtualDesktop = ({ onPlayerAction, playerName }) => {
  // Refs
  const desktopRef = useRef(null);
  const backgroundRef = useRef(null);
  
  // État local
  const [contextMenu, setContextMenu] = useState(null);
  const [selectedItems, setSelectedItems] = useState([]);
  const [draggedItem, setDraggedItem] = useState(null);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  
  // Stores
  const osStore = useOSStore();
  const gameStore = useGameStore();
  
  // Données du bureau
  const { 
    desktop, 
    files, 
    folders, 
    windows, 
    corruptionLevel, 
    corruptionEffects,
    theme 
  } = osStore;

  /**
   * Gestionnaire de clic droit pour le menu contextuel
   */
  const handleContextMenu = useCallback((event) => {
    event.preventDefault();
    
    const rect = desktopRef.current.getBoundingClientRect();
    const x = event.clientX - rect.left;
    const y = event.clientY - rect.top;
    
    setContextMenu({
      x,
      y,
      target: event.target,
      timestamp: Date.now()
    });
    
    onPlayerAction({
      type: 'context_menu_open',
      position: { x, y },
      is_meta_action: true
    });
  }, [onPlayerAction]);

  /**
   * Fermer le menu contextuel
   */
  const handleCloseContextMenu = useCallback(() => {
    setContextMenu(null);
  }, []);

  /**
   * Gestionnaire de clic sur le bureau
   */
  const handleDesktopClick = useCallback((event) => {
    // Fermer le menu contextuel si ouvert
    if (contextMenu) {
      setContextMenu(null);
    }
    
    // Désélectionner les éléments
    if (selectedItems.length > 0) {
      setSelectedItems([]);
    }
    
    // Enregistrer l'action
    onPlayerAction({
      type: 'desktop_click',
      position: { x: event.clientX, y: event.clientY },
      is_meta_action: false
    });
  }, [contextMenu, selectedItems, onPlayerAction]);

  /**
   * Gestionnaire de mouvement de souris
   */
  const handleMouseMove = useCallback((event) => {
    const rect = desktopRef.current.getBoundingClientRect();
    setMousePosition({
      x: event.clientX - rect.left,
      y: event.clientY - rect.top
    });
  }, []);

  /**
   * Gestionnaire d'action sur un fichier
   */
  const handleFileAction = useCallback((action, fileName, data = {}) => {
    const success = osStore.handleFileAction(action, fileName, data);
    
    onPlayerAction({
      type: `file_${action}`,
      target: fileName,
      success,
      is_obedient: action === 'delete', // Supprimer un fichier est "obéissant"
      is_meta_action: action === 'properties',
      data
    });
    
    return success;
  }, [osStore, onPlayerAction]);

  /**
   * Gestionnaire de sélection d'élément
   */
  const handleItemSelect = useCallback((itemId, isMultiple = false) => {
    if (isMultiple) {
      setSelectedItems(prev => 
        prev.includes(itemId) 
          ? prev.filter(id => id !== itemId)
          : [...prev, itemId]
      );
    } else {
      setSelectedItems([itemId]);
    }
  }, []);

  /**
   * Gestionnaire de drag & drop
   */
  const handleDragStart = useCallback((itemId, itemType) => {
    setDraggedItem({ id: itemId, type: itemType });
  }, []);

  const handleDragEnd = useCallback(() => {
    setDraggedItem(null);
  }, []);

  const handleDrop = useCallback((event) => {
    event.preventDefault();
    
    if (!draggedItem) return;
    
    const rect = desktopRef.current.getBoundingClientRect();
    const dropPosition = {
      x: event.clientX - rect.left,
      y: event.clientY - rect.top
    };
    
    onPlayerAction({
      type: 'item_moved',
      item: draggedItem,
      position: dropPosition,
      is_meta_action: true
    });
    
    setDraggedItem(null);
  }, [draggedItem, onPlayerAction]);

  /**
   * Calcul du style de fond d'écran avec corruption
   */
  const getBackgroundStyle = useCallback(() => {
    const bg = desktop.background;
    if (!bg) return {};
    
    let style = {
      backgroundImage: `url(/api/backgrounds/${bg.name || 'default'})`,
      backgroundSize: 'cover',
      backgroundPosition: 'center',
      backgroundRepeat: 'no-repeat'
    };
    
    // Appliquer les effets de corruption
    if (bg.corruption) {
      const { dead_pixels, color_shift } = bg.corruption;
      
      if (dead_pixels > 0) {
        style.filter = `contrast(${100 - dead_pixels}%) brightness(${100 - dead_pixels * 0.5}%)`;
      }
      
      if (color_shift > 0) {
        style.filter = (style.filter || '') + ` hue-rotate(${color_shift * 180}deg)`;
      }
    }
    
    return style;
  }, [desktop.background]);

  // Écouter les événements du DOM
  useEffect(() => {
    const desktop = desktopRef.current;
    if (!desktop) return;
    
    desktop.addEventListener('contextmenu', handleContextMenu);
    desktop.addEventListener('click', handleDesktopClick);
    desktop.addEventListener('mousemove', handleMouseMove);
    desktop.addEventListener('dragover', (e) => e.preventDefault());
    desktop.addEventListener('drop', handleDrop);
    
    return () => {
      desktop.removeEventListener('contextmenu', handleContextMenu);
      desktop.removeEventListener('click', handleDesktopClick);
      desktop.removeEventListener('mousemove', handleMouseMove);
      desktop.removeEventListener('dragover', (e) => e.preventDefault());
      desktop.removeEventListener('drop', handleDrop);
    };
  }, [handleContextMenu, handleDesktopClick, handleMouseMove, handleDrop]);

  // Appliquer les classes de corruption
  const getCorruptionClasses = () => {
    const classes = ['virtual-desktop'];
    
    if (corruptionLevel > 0.8) classes.push('corruption-critical');
    else if (corruptionLevel > 0.6) classes.push('corruption-high');
    else if (corruptionLevel > 0.3) classes.push('corruption-medium');
    else if (corruptionLevel > 0.1) classes.push('corruption-low');
    
    return classes.join(' ');
  };

  return (
    <div 
      ref={desktopRef}
      className={getCorruptionClasses()}
      style={getBackgroundStyle()}
      data-corruption-level={corruptionLevel.toFixed(2)}
    >
      {/* Fond d'écran avec overlay de corruption */}
      <div 
        ref={backgroundRef}
        className="desktop-background"
        style={getBackgroundStyle()}
      >
        {/* Overlay de pixels morts */}
        {corruptionLevel > 0.2 && (
          <div 
            className="dead-pixels-overlay"
            style={{
              opacity: Math.min(corruptionLevel * 2, 1),
              background: `radial-gradient(circle at ${Math.random() * 100}% ${Math.random() * 100}%, transparent 0%, black 1px)`
            }}
          />
        )}
      </div>

      {/* Widgets du bureau */}
      <div className="desktop-widgets">
        <AnimatePresence>
          {desktop.widgets?.map(widget => (
            <DesktopWidget
              key={widget.id}
              widget={widget}
              corruptionLevel={corruptionLevel}
              onAction={onPlayerAction}
            />
          ))}
        </AnimatePresence>
      </div>

      {/* Fichiers sur le bureau */}
      <div className="desktop-files">
        <AnimatePresence>
          {files?.map(file => (
            <DesktopFile
              key={file.name}
              file={file}
              isSelected={selectedItems.includes(file.name)}
              onSelect={handleItemSelect}
              onAction={handleFileAction}
              onDragStart={handleDragStart}
              onDragEnd={handleDragEnd}
              corruptionLevel={corruptionLevel}
            />
          ))}
        </AnimatePresence>
      </div>

      {/* Dossiers sur le bureau */}
      <div className="desktop-folders">
        <AnimatePresence>
          {folders?.map(folder => (
            <DesktopFolder
              key={folder.name}
              folder={folder}
              isSelected={selectedItems.includes(folder.name)}
              onSelect={handleItemSelect}
              onAction={handleFileAction}
              onDragStart={handleDragStart}
              onDragEnd={handleDragEnd}
              corruptionLevel={corruptionLevel}
            />
          ))}
        </AnimatePresence>
      </div>

      {/* Gestionnaire de fenêtres */}
      <WindowManager
        windows={windows}
        onPlayerAction={onPlayerAction}
        corruptionLevel={corruptionLevel}
      />

      {/* Menu contextuel */}
      <AnimatePresence>
        {contextMenu && (
          <ContextMenu
            position={{ x: contextMenu.x, y: contextMenu.y }}
            onClose={handleCloseContextMenu}
            onAction={onPlayerAction}
            target={contextMenu.target}
          />
        )}
      </AnimatePresence>

      {/* Informations de session (coin supérieur droit) */}
      <div className="session-info">
        <span>Session : {playerName || 'Joueur'}</span>
        {gameStore.showDebug && (
          <span className="debug-info">
            {Math.round(gameStore.timeElapsed)}s | {gameStore.currentPhase}
          </span>
        )}
      </div>

      {/* Overlay de glitch pour corruption extrême */}
      {corruptionLevel > 0.7 && (
        <div 
          className="glitch-overlay"
          style={{
            opacity: (corruptionLevel - 0.7) * 3.33, // 0 à 1 pour les 30% derniers
            animation: `glitch-lines ${0.5 / corruptionLevel}s infinite`
          }}
        />
      )}

      {/* Debug: Position de la souris */}
      {gameStore.showDebug && (
        <div className="mouse-debug">
          Mouse: {mousePosition.x}, {mousePosition.y}
        </div>
      )}
    </div>
  );
};

export default VirtualDesktop;
