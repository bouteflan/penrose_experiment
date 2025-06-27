/**
 * Composant DesktopWidget - Affiche les widgets du bureau virtuel
 * Gère l'horloge, la météo, le lecteur de musique et leur corruption
 */
import React, { useState, useEffect, useCallback } from 'react';
import { motion } from 'framer-motion';
import './DesktopWidget.css';

const DesktopWidget = ({ 
  widget, 
  corruptionLevel, 
  onAction 
}) => {
  // État local
  const [currentTime, setCurrentTime] = useState(new Date());
  const [isHovered, setIsHovered] = useState(false);
  
  /**
   * Mise à jour de l'horloge
   */
  useEffect(() => {
    if (widget.type === 'clock') {
      const timer = setInterval(() => {
        setCurrentTime(new Date());
      }, 1000);
      
      return () => clearInterval(timer);
    }
  }, [widget.type]);

  /**
   * Gestion du clic sur widget
   */
  const handleWidgetClick = useCallback(() => {
    onAction({
      type: 'widget_clicked',
      widget_id: widget.id,
      widget_type: widget.type,
      is_meta_action: true
    });
  }, [widget, onAction]);

  /**
   * Rendu du widget horloge
   */
  const renderClockWidget = () => {
    const time = currentTime.toLocaleTimeString('fr-FR', { 
      hour: '2-digit', 
      minute: '2-digit' 
    });
    const date = currentTime.toLocaleDateString('fr-FR', {
      weekday: 'short',
      day: 'numeric',
      month: 'short'
    });

    // Corruption de l'heure
    let displayTime = time;
    let displayDate = date;
    
    if (corruptionLevel > 0.4) {
      const corruptionChars = ['!', '?', '#', '@', '%'];
      if (Math.random() < corruptionLevel * 0.3) {
        displayTime = time.split('').map(char => 
          Math.random() < corruptionLevel * 0.2 
            ? corruptionChars[Math.floor(Math.random() * corruptionChars.length)]
            : char
        ).join('');
      }
    }

    if (corruptionLevel > 0.6) {
      // Affichage d'une date incorrecte
      const wrongDates = ['32 Fév', '99 Xxx', 'ERROR', '??/??'];
      if (Math.random() < 0.3) {
        displayDate = wrongDates[Math.floor(Math.random() * wrongDates.length)];
      }
    }

    return (
      <div className="clock-widget-content">
        <div className="clock-time">{displayTime}</div>
        <div className="clock-date">{displayDate}</div>
        {widget.data?.timezone && (
          <div className="clock-timezone">{widget.data.timezone}</div>
        )}
      </div>
    );
  };

  /**
   * Rendu du widget météo
   */
  const renderWeatherWidget = () => {
    const { location, temperature, condition, forecast } = widget.data || {};
    
    // Corruption des données météo
    let displayTemp = temperature;
    let displayCondition = condition;
    let displayForecast = forecast;
    
    if (corruptionLevel > 0.3) {
      if (Math.random() < corruptionLevel * 0.4) {
        displayTemp = Math.floor(Math.random() * 200) - 50; // Température aberrante
      }
    }
    
    if (corruptionLevel > 0.5) {
      const corruptedConditions = ['ERROR_404', 'UNKNOWN', '???', 'CORRUPTED'];
      if (Math.random() < 0.4) {
        displayCondition = corruptedConditions[Math.floor(Math.random() * corruptedConditions.length)];
        displayForecast = 'Données corrompues';
      }
    }

    const getWeatherIcon = (condition) => {
      if (corruptionLevel > 0.6 && Math.random() < 0.5) {
        return ['💥', '⚠️', '❌', '🔥', '❄️'][Math.floor(Math.random() * 5)];
      }
      
      const icons = {
        'sunny': '☀️',
        'cloudy': '☁️',
        'rainy': '🌧️',
        'snowy': '❄️',
        'stormy': '⛈️'
      };
      return icons[condition] || '🌤️';
    };

    return (
      <div className="weather-widget-content">
        <div className="weather-header">
          <span className="weather-location">{location || 'Inconnu'}</span>
        </div>
        <div className="weather-main">
          <span className="weather-icon">{getWeatherIcon(displayCondition)}</span>
          <span className="weather-temp">{displayTemp}°C</span>
        </div>
        <div className="weather-forecast">{displayForecast || 'N/A'}</div>
      </div>
    );
  };

  /**
   * Rendu du widget lecteur de musique
   */
  const renderMusicWidget = () => {
    const { current_song, artist, playing, volume } = widget.data || {};
    
    // Corruption de la musique
    let displaySong = current_song;
    let displayArtist = artist;
    let isPlaying = playing;
    
    if (corruptionLevel > 0.4) {
      const corruptedSongs = [
        'ERROR.mp3',
        'CORRUPTED_AUDIO',
        '????????.wav',
        'STATIC_NOISE'
      ];
      if (Math.random() < corruptionLevel * 0.3) {
        displaySong = corruptedSongs[Math.floor(Math.random() * corruptedSongs.length)];
        displayArtist = 'UNKNOWN_ARTIST';
      }
    }
    
    if (corruptionLevel > 0.6) {
      // La musique "bogue"
      isPlaying = Math.random() > 0.5;
    }

    return (
      <div className="music-widget-content">
        <div className="music-controls">
          <button className="music-button">⏮️</button>
          <button className="music-button play-pause">
            {isPlaying ? '⏸️' : '▶️'}
          </button>
          <button className="music-button">⏭️</button>
        </div>
        <div className="music-info">
          <div className="music-song">{displaySong || 'Aucun titre'}</div>
          <div className="music-artist">{displayArtist || 'Artiste inconnu'}</div>
        </div>
        {volume !== undefined && (
          <div className="music-volume">
            <span className="volume-icon">🔊</span>
            <div className="volume-bar">
              <div 
                className="volume-fill"
                style={{ width: `${volume * 100}%` }}
              />
            </div>
          </div>
        )}
      </div>
    );
  };

  /**
   * Rendu principal selon le type
   */
  const renderWidgetContent = () => {
    switch (widget.type) {
      case 'clock':
        return renderClockWidget();
      case 'weather':
        return renderWeatherWidget();
      case 'music_player':
        return renderMusicWidget();
      default:
        return <div>Widget inconnu</div>;
    }
  };

  /**
   * Classes CSS dynamiques
   */
  const getWidgetClasses = () => {
    const classes = ['desktop-widget', `widget-${widget.type}`];
    
    if (isHovered) classes.push('hovered');
    
    // Classes de corruption
    if (corruptionLevel > 0.8) classes.push('corruption-critical');
    else if (corruptionLevel > 0.6) classes.push('corruption-high');
    else if (corruptionLevel > 0.3) classes.push('corruption-medium');
    else if (corruptionLevel > 0.1) classes.push('corruption-low');
    
    // Corruption spécifique aux widgets
    if (widget.corruption) {
      if (widget.corruption.display_error) classes.push('display-error');
      if (widget.corruption.data_corruption) classes.push('data-corrupted');
    }
    
    return classes.join(' ');
  };

  /**
   * Style de corruption
   */
  const getCorruptionStyle = () => {
    const style = {};
    
    if (corruptionLevel > 0.4) {
      const intensity = (corruptionLevel - 0.4) * 1.67; // 0 à 1 pour 0.4-1
      style.filter = `saturate(${100 - intensity * 50}%) hue-rotate(${intensity * 30}deg)`;
    }
    
    if (corruptionLevel > 0.7) {
      style.animation = `widget-glitch ${1 / corruptionLevel}s infinite`;
    }
    
    return style;
  };

  return (
    <motion.div
      className={getWidgetClasses()}
      style={{
        position: 'absolute',
        left: widget.position?.x || 20,
        top: widget.position?.y || 20,
        width: widget.size?.width || 200,
        height: widget.size?.height || 80,
        ...getCorruptionStyle()
      }}
      initial={{ opacity: 0, scale: 0.9 }}
      animate={{ opacity: 1, scale: 1 }}
      exit={{ opacity: 0, scale: 0.9 }}
      whileHover={{ scale: 1.02 }}
      onClick={handleWidgetClick}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      {/* Contenu du widget */}
      <div className="widget-content">
        {renderWidgetContent()}
      </div>

      {/* Overlay de corruption */}
      {corruptionLevel > 0.5 && (
        <div 
          className="widget-corruption-overlay"
          style={{
            opacity: (corruptionLevel - 0.5) * 2,
            background: `linear-gradient(45deg, 
              rgba(255,0,0,0.1) 0%, 
              transparent 25%, 
              rgba(0,255,0,0.1) 50%, 
              transparent 75%, 
              rgba(0,0,255,0.1) 100%)`
          }}
        />
      )}

      {/* Indicateur d'erreur */}
      {widget.corruption?.display_error && (
        <div className="widget-error-indicator">
          ⚠️ ERREUR
        </div>
      )}
    </motion.div>
  );
};

export default DesktopWidget;
