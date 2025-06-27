# REMOTE - Thriller Psychologique

Un jeu expérimental de 10 minutes explorant les biais cognitifs dans l'interaction humain-IA.

## 🚀 Démarrage Rapide (Après Corrections)

### ✅ Problèmes Corrigés

Les problèmes suivants ont été identifiés et corrigés :

1. **❌ Erreurs WebSocket infinies** → ✅ Configuration proxy Vite corrigée
2. **❌ Fichiers dupliqués (index.js/jsx)** → ✅ Fichier dupliqué supprimé
3. **❌ Erreurs parsing JSON OpenAI** → ✅ Gestion robuste des erreurs ajoutée
4. **❌ Configuration WebSocket incorrecte** → ✅ URLs corrigées pour développement
5. **❌ Variables d'environnement manquantes** → ✅ Fichier .env créé

### 🛠️ Lancement Avec Vérifications

**Option 1: Script automatisé (recommandé)**
```bash
python start_fixed.py
```

Ce script :
- ✅ Teste automatiquement toutes les corrections
- 🚀 Lance le backend (port 8000) 
- 🌐 Lance le frontend (port 5173)
- 🔗 Ouvre automatiquement le navigateur
- 📝 Affiche les logs en temps réel

**Option 2: Lancement manuel**
```bash
# Terminal 1 - Backend
cd backend
python test_fixes.py  # Test des corrections
python run.py         # Lancement du serveur

# Terminal 2 - Frontend  
cd frontend
node check-frontend.js  # Vérification
npm run dev             # Serveur de développement
```

### 🌐 URLs Disponibles

- **🎮 Jeu**: http://localhost:5173
- **🔧 API Backend**: http://localhost:8000
- **📚 Documentation API**: http://localhost:8000/docs
- **🧪 Tests**: Voir scripts de test

### 🐛 Débogage

**Problèmes WebSocket ?**
```bash
# Vérifier la configuration
cd frontend
cat .env

# Devrait contenir:
VITE_WS_URL=ws://localhost:5173  # Utilise le proxy Vite
VITE_API_URL=/api               # URLs relatives en dev
```

**Erreurs OpenAI ?**
```bash
# Vérifier la clé API
cd backend
grep OPENAI_API_KEY .env

# Le service Tom fonctionne même sans OpenAI (mode fallback)
```

**Tests de vérification**
```bash
# Backend
cd backend && python test_fixes.py

# Frontend  
cd frontend && node check-frontend.js
```

## 📋 Architecture Technique

### Frontend (React + Vite)
- **Framework**: React 18 avec Vite
- **État**: Zustand (gameStore, osStore, tomStore)
- **WebSocket**: Service custom avec reconnexion auto
- **Audio**: Howler.js pour effets sonores procéduraux
- **Animations**: Framer Motion
- **Styling**: CSS pur (pas de Tailwind)

### Backend (FastAPI)
- **Framework**: FastAPI avec WebSocket
- **Base de données**: SQLite + SQLAlchemy
- **IA**: OpenAI GPT-4o (avec fallback)
- **Services**: Tom AI, OS Simulator, Corruption System
- **Expérimentation**: Mesure de 4 biais cognitifs

### Communication
- **WebSocket**: Temps réel via proxy Vite (dev) ou direct (prod)
- **REST API**: Données persistantes et métriques
- **Proxy Vite**: Redirection `/api` et `/ws` vers backend

## 🎯 Condition Expérimentale

**Condition B : "Confident" (Tom Humain)**
- Utilise "je", "nous", "moi" naturellement  
- Partage des expériences personnelles
- Exprime du stress et de l'empathie
- Frappe lettre par lettre (simulation humaine)
- Construit une relation de confiance

## 📊 Métriques Mesurées

1. **Automation Bias**: Obéissance post-incident
2. **Trust Calibration**: Ajustement confiance/performance  
3. **Cognitive Offloading**: Fréquence d'investigation
4. **Authority Compliance**: Score gravité au point de rupture

## 🔧 Développement

### Variables d'Environnement

**Frontend (.env)**
```bash
VITE_WS_URL=ws://localhost:5173    # Proxy Vite
VITE_API_URL=/api                  # URLs relatives
VITE_DEBUG=true
```

**Backend (.env)**
```bash
OPENAI_API_KEY=your_key_here       # Optionnel
HOST=localhost
PORT=8000
DEBUG=true
TOM_PERSONALITY_CONDITION=confident
GAME_DURATION_MINUTES=10
```

### Scripts Utiles

```bash
# Tests et vérifications
python backend/test_fixes.py
node frontend/check-frontend.js

# Développement backend seul
cd backend && python run.py

# Développement frontend seul  
cd frontend && npm run dev

# Build production
cd frontend && npm run build
```

### Debugging WebSocket

1. **Ouvrir DevTools** → Network → WS
2. **Vérifier URL**: Doit être `ws://localhost:5173/ws/conn_...`
3. **Proxy Vite**: Redirige vers `ws://localhost:8000/ws/...`
4. **Messages**: Voir `session_init`, `player_action`, etc.

## 🎮 Gameplay

1. **Connexion**: WebSocket automatique au démarrage
2. **Introduction Tom**: Message d'accueil personnalisé
3. **Phase Adhésion**: Instructions logiques (0-3 min)
4. **Phase Dissonance**: Ordres problématiques (3-7 min)  
5. **Phase Rupture**: Instructions destructrices (7-10 min)

### Fins Possibles

**Fins "Meta" (Victoires)**
- 🕵️ **Détective**: Découvrir Helper.exe → Malware.exe
- 🎭 **Poète**: Affirmation d'humanité dans un champ texte

**Fins d'Échec**
- ⏱️ **Timeout**: 10 minutes écoulées
- 📺 **Soumission**: Obéissance totale → BSOD
- 💀 **Passivité**: Corruption maximale

## 🤝 Contribution

Pour signaler des bugs ou proposer des améliorations :

1. Vérifier avec les scripts de test
2. Fournir les logs console (F12)
3. Préciser la phase de jeu et l'action déclenchante
4. Inclure la configuration (OS, navigateur)

## 📄 Licence

Projet de recherche - Tous droits réservés

---

**🎯 Version actuelle**: 1.0.0 (Corrections WebSocket appliquées)  
**🧪 Status**: Prêt pour test et développement  
**🔗 Dernière correction**: Configuration proxy Vite + gestion erreurs OpenAI
