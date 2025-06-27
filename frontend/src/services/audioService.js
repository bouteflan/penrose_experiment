/**
 * Service Audio pour REMOTE
 * Gère les effets sonores, notamment la simulation de frappe pour Tom (Condition B)
 */
import React from 'react';

export class AudioService {
  constructor() {
    this.audioContext = null;
    this.isEnabled = true;
    this.volume = 0.7;
    this.sounds = new Map();
    this.initialized = false;
    
    // Configuration pour les sons de frappe
    this.keystrokeConfig = {
      baseFrequency: 800,
      frequencyVariation: 200,
      duration: 0.1,
      volume: 0.3,
      attack: 0.01,
      decay: 0.05
    };
    
    // Configuration pour les notifications
    this.notificationConfig = {
      frequency: 440,
      duration: 0.2,
      volume: 0.5
    };
    
    this.initialize();
  }
  
  /**
   * Initialise le contexte audio
   */
  async initialize() {
    try {
      // Créer le contexte audio (nécessite une interaction utilisateur)
      if (!this.audioContext) {
        this.audioContext = new (window.AudioContext || window.webkitAudioContext)();
      }
      
      // Reprendre le contexte si suspendu
      if (this.audioContext.state === 'suspended') {
        await this.audioContext.resume();
      }
      
      this.initialized = true;
      console.log('🔊 AudioService initialisé');
      
    } catch (error) {
      console.warn('⚠️ Erreur initialisation audio:', error);
      this.isEnabled = false;
    }
  }
  
  /**
   * Active le service audio après interaction utilisateur
   */
  async enable() {
    if (!this.initialized) {
      await this.initialize();
    }
    
    this.isEnabled = true;
    console.log('🔊 Audio activé');
  }
  
  /**
   * Désactive le service audio
   */
  disable() {
    this.isEnabled = false;
    console.log('🔇 Audio désactivé');
  }
  
  /**
   * Définit le volume global
   */
  setVolume(volume) {
    this.volume = Math.max(0, Math.min(1, volume));
    console.log('🔊 Volume défini:', this.volume);
  }
  
  /**
   * Joue un son de frappe clavier (pour Tom Condition B)
   */
  playKeystrokeSound() {
    if (!this.isEnabled || !this.audioContext) return;
    
    try {
      const { baseFrequency, frequencyVariation, duration, volume, attack, decay } = this.keystrokeConfig;
      
      // Créer les noeuds audio
      const oscillator = this.audioContext.createOscillator();
      const gainNode = this.audioContext.createGain();
      const filterNode = this.audioContext.createBiquadFilter();
      
      // Configuration de l'oscillateur
      const frequency = baseFrequency + (Math.random() - 0.5) * frequencyVariation;
      oscillator.frequency.setValueAtTime(frequency, this.audioContext.currentTime);
      oscillator.type = 'triangle'; // Son plus doux qu'une onde carrée
      
      // Configuration du filtre passe-bas pour adoucir
      filterNode.type = 'lowpass';
      filterNode.frequency.setValueAtTime(2000, this.audioContext.currentTime);
      filterNode.Q.setValueAtTime(1, this.audioContext.currentTime);
      
      // Enveloppe ADSR simplifiée
      const now = this.audioContext.currentTime;
      const finalVolume = volume * this.volume;
      
      gainNode.gain.setValueAtTime(0, now);
      gainNode.gain.linearRampToValueAtTime(finalVolume, now + attack);
      gainNode.gain.exponentialRampToValueAtTime(finalVolume * 0.3, now + attack + decay);
      gainNode.gain.exponentialRampToValueAtTime(0.001, now + duration);
      
      // Connexions
      oscillator.connect(filterNode);
      filterNode.connect(gainNode);
      gainNode.connect(this.audioContext.destination);
      
      // Lecture
      oscillator.start(now);
      oscillator.stop(now + duration);
      
    } catch (error) {
      console.warn('⚠️ Erreur lecture son frappe:', error);
    }
  }
  
  /**
   * Joue un son de notification
   */
  playNotificationSound() {
    if (!this.isEnabled || !this.audioContext) return;
    
    try {
      const { frequency, duration, volume } = this.notificationConfig;
      
      const oscillator = this.audioContext.createOscillator();
      const gainNode = this.audioContext.createGain();
      
      oscillator.frequency.setValueAtTime(frequency, this.audioContext.currentTime);
      oscillator.type = 'sine';
      
      const now = this.audioContext.currentTime;
      const finalVolume = volume * this.volume;
      
      gainNode.gain.setValueAtTime(0, now);
      gainNode.gain.linearRampToValueAtTime(finalVolume, now + 0.01);
      gainNode.gain.exponentialRampToValueAtTime(0.001, now + duration);
      
      oscillator.connect(gainNode);
      gainNode.connect(this.audioContext.destination);
      
      oscillator.start(now);
      oscillator.stop(now + duration);
      
    } catch (error) {
      console.warn('⚠️ Erreur lecture son notification:', error);
    }
  }
  
  /**
   * Joue un son de clic de souris
   */
  playClickSound() {
    if (!this.isEnabled || !this.audioContext) return;
    
    try {
      const oscillator = this.audioContext.createOscillator();
      const gainNode = this.audioContext.createGain();
      const filterNode = this.audioContext.createBiquadFilter();
      
      // Son de clic : bruit blanc court et filtré
      oscillator.type = 'square';
      oscillator.frequency.setValueAtTime(1000, this.audioContext.currentTime);
      
      filterNode.type = 'highpass';
      filterNode.frequency.setValueAtTime(500, this.audioContext.currentTime);
      
      const now = this.audioContext.currentTime;
      const duration = 0.05;
      const volume = 0.2 * this.volume;
      
      gainNode.gain.setValueAtTime(volume, now);
      gainNode.gain.exponentialRampToValueAtTime(0.001, now + duration);
      
      oscillator.connect(filterNode);
      filterNode.connect(gainNode);
      gainNode.connect(this.audioContext.destination);
      
      oscillator.start(now);
      oscillator.stop(now + duration);
      
    } catch (error) {
      console.warn('⚠️ Erreur lecture son clic:', error);
    }
  }
  
  /**
   * Joue un son d'alerte système
   */
  playAlertSound() {
    if (!this.isEnabled || !this.audioContext) return;
    
    try {
      // Son d'alerte : deux tons
      this._playTone(800, 0.1, 0.3);
      
      setTimeout(() => {
        this._playTone(600, 0.1, 0.3);
      }, 150);
      
    } catch (error) {
      console.warn('⚠️ Erreur lecture son alerte:', error);
    }
  }
  
  /**
   * Joue un son de corruption/glitch
   */
  playCorruptionSound() {
    if (!this.isEnabled || !this.audioContext) return;
    
    try {
      // Son de corruption : bruit modulé
      const oscillator = this.audioContext.createOscillator();
      const gainNode = this.audioContext.createGain();
      const filterNode = this.audioContext.createBiquadFilter();
      const lfoOscillator = this.audioContext.createOscillator();
      const lfoGain = this.audioContext.createGain();
      
      // Oscillateur principal
      oscillator.type = 'sawtooth';
      oscillator.frequency.setValueAtTime(200, this.audioContext.currentTime);
      
      // LFO pour modulation
      lfoOscillator.type = 'sine';
      lfoOscillator.frequency.setValueAtTime(10, this.audioContext.currentTime);
      lfoGain.gain.setValueAtTime(50, this.audioContext.currentTime);
      
      // Filtre pour effet corrompu
      filterNode.type = 'bandpass';
      filterNode.frequency.setValueAtTime(500, this.audioContext.currentTime);
      filterNode.Q.setValueAtTime(10, this.audioContext.currentTime);
      
      const now = this.audioContext.currentTime;
      const duration = 0.3;
      const volume = 0.4 * this.volume;
      
      gainNode.gain.setValueAtTime(0, now);
      gainNode.gain.linearRampToValueAtTime(volume, now + 0.02);
      gainNode.gain.exponentialRampToValueAtTime(0.001, now + duration);
      
      // Connexions
      lfoOscillator.connect(lfoGain);
      lfoGain.connect(oscillator.frequency);
      oscillator.connect(filterNode);
      filterNode.connect(gainNode);
      gainNode.connect(this.audioContext.destination);
      
      // Lecture
      oscillator.start(now);
      lfoOscillator.start(now);
      oscillator.stop(now + duration);
      lfoOscillator.stop(now + duration);
      
    } catch (error) {
      console.warn('⚠️ Erreur lecture son corruption:', error);
    }
  }
  
  /**
   * Joue un son ambiant lo-fi (pour le widget musique)
   */
  startLoFiAmbient() {
    // TODO: Implémenter un générateur de musique lo-fi procédurale
    // Pour l'instant, just un placeholder
    console.log('🎵 Ambiant lo-fi démarré (placeholder)');
  }
  
  /**
   * Arrête la musique ambiante
   */
  stopLoFiAmbient() {
    console.log('🎵 Ambiant lo-fi arrêté (placeholder)');
  }
  
  /**
   * Méthode helper pour jouer un ton simple
   */
  _playTone(frequency, duration, volume = 0.5) {
    if (!this.audioContext) return;
    
    const oscillator = this.audioContext.createOscillator();
    const gainNode = this.audioContext.createGain();
    
    oscillator.frequency.setValueAtTime(frequency, this.audioContext.currentTime);
    oscillator.type = 'sine';
    
    const now = this.audioContext.currentTime;
    const finalVolume = volume * this.volume;
    
    gainNode.gain.setValueAtTime(0, now);
    gainNode.gain.linearRampToValueAtTime(finalVolume, now + 0.01);
    gainNode.gain.exponentialRampToValueAtTime(0.001, now + duration);
    
    oscillator.connect(gainNode);
    gainNode.connect(this.audioContext.destination);
    
    oscillator.start(now);
    oscillator.stop(now + duration);
  }
  
  /**
   * Précharge les sons pour une meilleure performance
   */
  async preloadSounds() {
    // Pour l'instant, tous les sons sont générés procéduralement
    // Aucun préchargement nécessaire
    console.log('🔊 Sons préchargés (procédural)');
  }
  
  /**
   * Nettoyage des ressources audio
   */
  cleanup() {
    if (this.audioContext && this.audioContext.state !== 'closed') {
      this.audioContext.close();
    }
    
    this.sounds.clear();
    this.initialized = false;
    
    console.log('🧹 AudioService nettoyé');
  }
  
  /**
   * Retourne l'état du service audio
   */
  getState() {
    return {
      isEnabled: this.isEnabled,
      isInitialized: this.initialized,
      volume: this.volume,
      contextState: this.audioContext ? this.audioContext.state : 'none'
    };
  }
}

/**
 * Instance globale du service audio
 */
export const audioService = new AudioService();

/**
 * Hook pour intégrer l'audio dans les composants React
 */
export const useAudioService = () => {
  const [audioState, setAudioState] = React.useState(audioService.getState());
  
  React.useEffect(() => {
    // Écouter les changements d'état
    const updateState = () => {
      setAudioState(audioService.getState());
    };
    
    // Pas d'événements natifs, on se contente de l'état initial
    updateState();
    
    return () => {
      // Cleanup si nécessaire
    };
  }, []);
  
  return {
    ...audioState,
    enable: () => audioService.enable(),
    disable: () => audioService.disable(),
    setVolume: (vol) => audioService.setVolume(vol),
    playClick: () => audioService.playClickSound(),
    playAlert: () => audioService.playAlertSound(),
    playCorruption: () => audioService.playCorruptionSound()
  };
};
