/**
 * Service WebSocket pour la communication temps réel avec le backend
 * Gère la connexion, reconnexion automatique et distribution des messages
 */

export class WebSocketService {
  constructor(wsUrl) {
    this.baseWsUrl = wsUrl;
    this.ws = null;
    this.isConnected = false;
    this.reconnectAttempts = 0;
    this.maxReconnectAttempts = 5;
    this.reconnectDelay = 1000; // 1 seconde initiale
    this.messageQueue = [];
    this.listeners = new Map();
    this.connectionPromise = null;
    
    // Générer un ID de connexion unique
    this.connectionId = `conn_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
    
    // URL complète avec connection_id
    this.wsUrl = `${this.baseWsUrl}/ws/${this.connectionId}`;
    
    // Statistiques
    this.stats = {
      messagesReceived: 0,
      messagesSent: 0,
      reconnections: 0,
      lastMessageTime: null
    };
    
    console.log('🔌 WebSocket Service créé:', this.connectionId);
    
    this.connect();
  }
  
  /**
   * Établit la connexion WebSocket
   */
  async connect() {
    if (this.connectionPromise) {
      return this.connectionPromise;
    }
    
    this.connectionPromise = new Promise((resolve, reject) => {
      try {
        console.log('🔌 Connexion WebSocket...', this.wsUrl);
        
        this.ws = new WebSocket(this.wsUrl);
        
        // Événement de connexion
        this.ws.onopen = () => {
          console.log('✅ WebSocket connecté');
          this.isConnected = true;
          this.reconnectAttempts = 0;
          this.reconnectDelay = 1000;
          
          // Envoyer les messages en queue
          this._flushMessageQueue();
          
          // Notifier les listeners
          this._notifyListeners('connection', { status: 'connected' });
          
          resolve();
        };
        
        // Réception de messages
        this.ws.onmessage = (event) => {
          try {
            const data = JSON.parse(event.data);
            this._handleMessage(data);
          } catch (error) {
            console.error('❌ Erreur parsing message WebSocket:', error);
          }
        };
        
        // Gestion des erreurs
        this.ws.onerror = (error) => {
          console.error('❌ Erreur WebSocket:', error);
          this._notifyListeners('error', { error });
        };
        
        // Fermeture de connexion
        this.ws.onclose = (event) => {
          console.log('🔌 WebSocket fermé:', event.code, event.reason);
          this.isConnected = false;
          this.connectionPromise = null;
          
          this._notifyListeners('disconnection', { 
            code: event.code, 
            reason: event.reason 
          });
          
          // Reconnexion automatique si pas de fermeture intentionnelle
          if (event.code !== 1000 && this.reconnectAttempts < this.maxReconnectAttempts) {
            this._scheduleReconnect();
          } else if (this.reconnectAttempts >= this.maxReconnectAttempts) {
            console.error('❌ Nombre maximum de tentatives de reconnexion atteint');
            reject(new Error('Max reconnection attempts reached'));
          }
        };
        
      } catch (error) {
        console.error('❌ Erreur création WebSocket:', error);
        this.connectionPromise = null;
        reject(error);
      }
    });
    
    return this.connectionPromise;
  }
  
  /**
   * Ferme la connexion WebSocket
   */
  disconnect() {
    if (this.ws) {
      console.log('🔌 Fermeture WebSocket...');
      this.ws.close(1000, 'Client disconnect');
      this.ws = null;
      this.isConnected = false;
      this.connectionPromise = null;
    }
  }
  
  /**
   * Envoie un message via WebSocket
   */
  send(message) {
    if (!this.isConnected || !this.ws) {
      // Ajouter à la queue si pas connecté
      this.messageQueue.push(message);
      console.log('📤 Message ajouté à la queue (déconnecté):', message.type);
      
      // Tenter de reconnecter
      this.connect();
      return;
    }
    
    try {
      const messageString = JSON.stringify(message);
      this.ws.send(messageString);
      
      this.stats.messagesSent++;
      this.stats.lastMessageTime = new Date();
      
      console.log('📤 Message envoyé:', message.type);
      
    } catch (error) {
      console.error('❌ Erreur envoi message:', error);
      // Ajouter à la queue pour retry
      this.messageQueue.push(message);
    }
  }
  
  /**
   * Ajoute un listener pour un type de message
   */
  addListener(messageType, callback) {
    if (!this.listeners.has(messageType)) {
      this.listeners.set(messageType, []);
    }
    
    this.listeners.get(messageType).push(callback);
    
    // Retourner une fonction pour retirer le listener
    return () => {
      const callbacks = this.listeners.get(messageType);
      if (callbacks) {
        const index = callbacks.indexOf(callback);
        if (index > -1) {
          callbacks.splice(index, 1);
        }
      }
    };
  }
  
  /**
   * Retire tous les listeners d'un type
   */
  removeListeners(messageType) {
    this.listeners.delete(messageType);
  }
  
  /**
   * Retourne l'état de la connexion
   */
  getConnectionState() {
    return {
      isConnected: this.isConnected,
      connectionId: this.connectionId,
      reconnectAttempts: this.reconnectAttempts,
      queueSize: this.messageQueue.length,
      stats: { ...this.stats }
    };
  }
  
  /**
   * Vide la queue des messages en attente
   */
  _flushMessageQueue() {
    console.log(`📤 Envoi de ${this.messageQueue.length} messages en queue`);
    
    while (this.messageQueue.length > 0 && this.isConnected) {
      const message = this.messageQueue.shift();
      this.send(message);
    }
  }
  
  /**
   * Traite un message reçu
   */
  _handleMessage(data) {
    this.stats.messagesReceived++;
    this.stats.lastMessageTime = new Date();
    
    console.log('📥 Message reçu:', data.type);
    
    // Notifier les listeners spécifiques
    this._notifyListeners(data.type, data);
    
    // Notifier les listeners génériques
    this._notifyListeners('message', data);
  }
  
  /**
   * Notifie les listeners d'un type donné
   */
  _notifyListeners(messageType, data) {
    const callbacks = this.listeners.get(messageType);
    if (callbacks) {
      callbacks.forEach(callback => {
        try {
          callback(data);
        } catch (error) {
          console.error(`❌ Erreur dans listener ${messageType}:`, error);
        }
      });
    }
  }
  
  /**
   * Programme une tentative de reconnexion
   */
  _scheduleReconnect() {
    this.reconnectAttempts++;
    const delay = Math.min(this.reconnectDelay * Math.pow(2, this.reconnectAttempts - 1), 30000);
    
    console.log(`🔄 Reconnexion dans ${delay}ms (tentative ${this.reconnectAttempts}/${this.maxReconnectAttempts})`);
    
    setTimeout(() => {
      if (!this.isConnected) {
        this.stats.reconnections++;
        this.connect();
      }
    }, delay);
  }
}

/**
 * Factory pour créer une instance WebSocket configurée
 */
export const createWebSocketService = (config) => {
  const wsUrl = config.wsUrl || 'ws://localhost:8000';
  return new WebSocketService(wsUrl);
};

/**
 * Hook pour intégrer le WebSocket dans les stores Zustand
 */
export const useWebSocketIntegration = (wsService, store) => {
  if (!wsService || !store) return;
  
  // Écouter les messages pour ce store
  const removeListener = wsService.addListener('message', (data) => {
    // Router les messages vers le bon store selon le type
    switch (data.type) {
      case 'tom_message_generated':
        if (store.handleGeneratedMessage) {
          store.handleGeneratedMessage(data.message_data);
        }
        break;
        
      case 'corruption_update':
        if (store.applyCorruption) {
          store.applyCorruption(data.corruption_data);
        }
        break;
        
      case 'os_state_update':
        if (store._loadOSState) {
          store._loadOSState(data.os_state);
        }
        break;
        
      case 'session_status':
        if (store.updateSessionStatus) {
          store.updateSessionStatus(data.status);
        }
        break;
        
      default:
        console.log('Message WebSocket non traité:', data.type);
    }
  });
  
  // Retourner la fonction de nettoyage
  return removeListener;
};
