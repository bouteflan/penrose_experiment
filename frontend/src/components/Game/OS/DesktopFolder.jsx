/**
 * Composant DesktopFolder - Représente un dossier sur le bureau virtuel
 * Similaire à DesktopFile mais avec des comportements spécifiques aux dossiers
 */
import React, { useState, useRef, useCallback } from 'react';
import { motion } from 'framer-motion';
import './DesktopFolder.css';

const DesktopFolder = ({
  folder,
  isSelected,
  onSelect,
  onAction,
  onDragStart,
  onDragEnd,
  corruptionLevel
}) => {
  // État local
  const [isHovered, setIsHovered] = useState(false);
  const [isDragging, setIsDragging] = useState(false);
  const [lastClickTime, setLastClickTime] = useState(0);
  
  // Refs
  const folderRef = useRef(null);
  
  /**
   * Obtient l'icône du dossier selon son type et état
   */
  const getFolderIcon = useCallback(() => {
    const { type, icon, protected: isProtected } = folder;
    
    // Dossiers corrompus
    if (corruptionLevel > 0.5 && Math.random() > 0.8) {
      return '💥';
    }
    
    // Icônes spéciales par type
    const iconMap = {
      'folder_documents': '📁',
      'folder_downloads': '📥',
      'folder_pictures': '🖼️',
      'folder_videos': '🎬',
      'folder_music': '🎵',
      'folder_desktop': '🖥️',
      'recycle_bin_empty': '🗑️',
      'recycle_bin_full': '🗑️',
      'system_folder': '⚙️',
      'network_folder': '🌐'
    };
    
    let baseIcon = iconMap[icon] || iconMap[type] || '📁';
    
    // Dossier protégé
    if (isProtected) {
      baseIcon = '🔐';
    }
    
    // Corbeille avec contenu
    if (type === 'recycle_bin' && folder.itemCount > 0) {
      baseIcon = '🗑️';
    }
    
    return baseIcon;
  }, [folder, corruptionLevel]);

  /**
   * Obtient le nom d'affichage avec corruption
   */
  const getDisplayName = useCallback(() => {
    let name = folder.name;
    
    // Corruption du nom
    if (corruptionLevel > 0.6) {
      const corruptionChars = ['░', '▒', '▓', '█', '?', '#'];
      const corruptionChance = (corruptionLevel - 0.6) * 2.5;
      
      name = name.split('').map(char => {
        if (Math.random() < corruptionChance * 0.25) {
          return corruptionChars[Math.floor(Math.random() * corruptionChars.length)];
        }
        return char;
      }).join('');
    }
    
    return name;
  }, [folder.name, corruptionLevel]);

  /**
   * Gestionnaire de clic
   */
  const handleClick = useCallback((event) => {
    event.stopPropagation();
    
    const now = Date.now();
    const timeDiff = now - lastClickTime;
    setLastClickTime(now);
    
    // Double-clic
    if (timeDiff < 500) {
      // Action spéciale pour la corbeille
      if (folder.type === 'recycle_bin') {
        onAction('open_recycle_bin', folder.name);
      } else {
        onAction('open_folder', folder.name);
      }
    } else {
      // Simple clic - sélection
      onSelect(folder.name, event.ctrlKey || event.metaKey);
    }
  }, [folder, onSelect, onAction, lastClickTime]);

  /**
   * Gestionnaire de clic droit
   */
  const handleContextMenu = useCallback((event) => {
    event.preventDefault();
    event.stopPropagation();
    
    if (!isSelected) {
      onSelect(folder.name, false);
    }
  }, [folder.name, isSelected, onSelect]);

  /**
   * Gestionnaires de drag & drop
   */
  const handleDragStart = useCallback((event) => {
    // La corbeille et les dossiers système ne peuvent pas être déplacés
    if (folder.type === 'recycle_bin' || folder.protected) {
      event.preventDefault();
      return;
    }
    
    setIsDragging(true);
    onDragStart(folder.name, 'folder');
    
    event.dataTransfer.setData('text/plain', folder.name);
    event.dataTransfer.setData('application/json', JSON.stringify(folder));
    event.dataTransfer.effectAllowed = 'move';
  }, [folder, onDragStart]);

  const handleDragEnd = useCallback(() => {
    setIsDragging(false);
    onDragEnd();
  }, [onDragEnd]);

  /**
   * Gestion du drop sur le dossier
   */
  const handleDragOver = useCallback((event) => {
    // Autoriser le drop sur les dossiers
    if (folder.type !== 'recycle_bin' && !folder.protected) {
      event.preventDefault();
    }
  }, [folder]);

  const handleDrop = useCallback((event) => {
    event.preventDefault();
    event.stopPropagation();
    
    const droppedData = event.dataTransfer.getData('application/json');
    if (droppedData) {
      const droppedItem = JSON.parse(droppedData);
      onAction('drop_on_folder', folder.name, { droppedItem });
    }
  }, [folder.name, onAction]);

  /**
   * Style de corruption
   */
  const getCorruptionStyle = useCallback(() => {
    const style = {};
    
    if (corruptionLevel > 0.3) {
      const desaturation = Math.min((corruptionLevel - 0.3) * 1.43, 1);
      style.filter = `saturate(${100 - desaturation * 60}%)`;
    }
    
    if (corruptionLevel > 0.5) {
      const rotation = (corruptionLevel - 0.5) * 8 * (Math.random() - 0.5);
      style.transform = `rotate(${rotation}deg)`;
    }
    
    if (corruptionLevel > 0.7) {
      style.animation = `folder-corruption ${1.2 / corruptionLevel}s infinite`;
    }
    
    return style;
  }, [corruptionLevel]);

  /**
   * Classes CSS dynamiques
   */
  const getClassNames = useCallback(() => {
    const classes = ['desktop-folder'];
    
    if (isSelected) classes.push('selected');
    if (isHovered) classes.push('hovered');
    if (isDragging) classes.push('dragging');
    if (folder.protected) classes.push('protected');
    if (folder.type === 'recycle_bin') classes.push('recycle-bin');
    
    // Classes de corruption
    if (corruptionLevel > 0.8) classes.push('corruption-critical');
    else if (corruptionLevel > 0.6) classes.push('corruption-high');
    else if (corruptionLevel > 0.3) classes.push('corruption-medium');
    else if (corruptionLevel > 0.1) classes.push('corruption-low');
    
    return classes.join(' ');
  }, [isSelected, isHovered, isDragging, folder, corruptionLevel]);

  /**
   * Contenu de l'info-bulle
   */
  const getTooltipContent = useCallback(() => {
    const content = {
      name: folder.name,
      type: folder.type === 'recycle_bin' ? 'Corbeille' : 'Dossier',
      protected: folder.protected
    };
    
    if (folder.type === 'recycle_bin' && folder.itemCount !== undefined) {
      content.items = `${folder.itemCount} élément(s)`;
    }
    
    if (corruptionLevel > 0.3) {
      content.corruption = 'Corruption détectée';
    }
    
    return content;
  }, [folder, corruptionLevel]);

  return (
    <motion.div
      ref={folderRef}
      className={getClassNames()}
      style={{
        position: 'absolute',
        left: folder.position?.x || 50,
        top: folder.position?.y || 50,
        ...getCorruptionStyle()
      }}
      initial={{ opacity: 0, scale: 0.8 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.8 }}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      drag={!folder.protected && folder.type !== 'recycle_bin'}
      dragMomentum={false}
      onDragStart={handleDragStart}
      onDragEnd={handleDragEnd}
      onDragOver={handleDragOver}
      onDrop={handleDrop}
      onClick={handleClick}
      onContextMenu={handleContextMenu}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      title={`${folder.name}${folder.type === 'recycle_bin' ? ` (${folder.itemCount || 0} éléments)` : ''}`}
    >
      {/* Icône du dossier */}
      <div className="folder-icon">
        <span className="icon-emoji">
          {getFolderIcon()}
        </span>
        
        {/* Badge de protection */}
        {folder.protected && (
          <span className="protection-badge">🔒</span>
        )}
        
        {/* Indicateur de contenu (corbeille) */}
        {folder.type === 'recycle_bin' && folder.itemCount > 0 && (
          <span className="content-badge">{folder.itemCount}</span>
        )}
        
        {/* Indicateur de corruption */}
        {corruptionLevel > 0.4 && (
          <span className="corruption-indicator">⚠️</span>
        )}
      </div>

      {/* Nom du dossier */}
      <div className="folder-name">
        <span>{getDisplayName()}</span>
      </div>

      {/* Info-bulle détaillée */}
      {isHovered && (
        <motion.div
          className="folder-tooltip"
          initial={{ opacity: 0, y: 10 }}
          animate={{ opacity: 1, y: 0 }}
          exit={{ opacity: 0, y: 10 }}
        >
          <div className="tooltip-content">
            {Object.entries(getTooltipContent()).map(([key, value]) => (
              <div key={key}>
                {key === 'name' && <strong>{value}</strong>}
                {key === 'type' && `Type: ${value}`}
                {key === 'items' && `Contenu: ${value}`}
                {key === 'protected' && value && '🔒 Dossier protégé'}
                {key === 'corruption' && `⚠️ ${value}`}
              </div>
            ))}
          </div>
        </motion.div>
      )}

      {/* Effet de sélection */}
      {isSelected && (
        <motion.div
          className="selection-overlay"
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          exit={{ opacity: 0 }}
        />
      )}

      {/* Zone de drop */}
      <div className="drop-zone" />

      {/* Effet de corruption visuelle */}
      {corruptionLevel > 0.6 && (
        <div 
          className="corruption-overlay"
          style={{
            opacity: (corruptionLevel - 0.6) * 2.5,
            background: `repeating-linear-gradient(
              45deg,
              rgba(255,0,0,0.2) 0px,
              transparent 2px,
              transparent 4px,
              rgba(0,255,0,0.2) 6px,
              transparent 8px,
              transparent 10px,
              rgba(0,0,255,0.2) 12px
            )`
          }}
        />
      )}
    </motion.div>
  );
};

export default DesktopFolder;
