# REMOTE - Psychological Thriller Game

## 🎮 Description

REMOTE est un thriller psychologique de 10 minutes qui se déroule dans une simulation d'interface de bureau. Le joueur, croyant son ordinateur piraté, reçoit l'aide d'un agent conversationnel nommé Tom. Ce jeu explore les biais cognitifs et la manipulation algorithmique.

## 🛠️ Stack Technique

- **Backend**: FastAPI + SQLite + WebSocket + GPT-4o
- **Frontend**: React 18 + Vite + Zustand + CSS pur
- **Base de données**: SQLite
- **Communication**: WebSocket temps réel

## 📋 Prérequis

- Python 3.9+ 
- Node.js 18+
- npm ou yarn
- Clé API OpenAI (GPT-4o)

## 🚀 Installation

### 1. Cloner et préparer l'environnement

```bash
cd C:\Users\antoi\Documents\dev\remote-game
```

### 2. Configuration Backend

```bash
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
```

### 3. Configuration Frontend

```bash
cd ..\frontend
npm install
```

### 4. Configuration des variables d'environnement

Copier `.env.example` vers `.env` et configurer :
- `OPENAI_API_KEY`: Votre clé API OpenAI
- `SECRET_KEY`: Clé secrète pour JWT
- `DATABASE_URL`: Chemin vers la base SQLite

### 5. Initialisation de la base de données

```bash
cd ..\backend
python scripts\init_db.py
```

### 6. Lancement en développement

**Terminal 1 - Backend:**
```bash
cd backend
venv\Scripts\activate
python run.py
```

**Terminal 2 - Frontend:**
```bash
cd frontend
npm run dev
```

L'application sera disponible sur `http://localhost:5173`

## 📁 Structure du Projet

Voir `docs/ARCHITECTURE.md` pour la documentation complète de l'architecture.

## 🧠 Fonctionnalités Clés

- Simulation d'OS réaliste
- IA conversationnelle avec GPT-4o
- Système de corruption visuelle progressive
- Mesure des biais cognitifs en temps réel
- Fins multiples selon les actions du joueur

## 📊 Collecte de Données

Le jeu collecte de manière anonyme :
- Temps de réaction aux instructions
- Patterns de comportement
- Métriques des biais cognitifs
- Points de rupture comportementaux

## 🎯 Objectifs de Recherche

Étude des 4 biais cognitifs principaux :
1. **Automation Bias** : Confiance excessive dans les systèmes automatisés
2. **Trust Calibration** : Capacité d'ajustement de la confiance
3. **Cognitive Offloading** : Délégation de la charge cognitive
4. **Authority Compliance** : Soumission à l'autorité algorithmique

## 🔧 Développement

### Scripts utiles

- `npm run dev` : Lancement frontend en développement
- `python run.py` : Lancement backend
- `python scripts/dev_server.py` : Serveur de développement complet
- `npm run build` : Build de production

### Tests

```bash
# Tests backend
cd backend && python -m pytest

# Tests frontend  
cd frontend && npm test
```

## 📝 Licence

Ce projet est développé à des fins de recherche sur l'interaction humain-IA.

## 🤝 Contribution

Ce projet est en développement actif. Voir `CONTRIBUTING.md` pour les guidelines.
