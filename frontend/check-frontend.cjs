#!/usr/bin/env node
/**
 * Script de vérification du frontend REMOTE
 */

const fs = require('fs');
const path = require('path');

function checkFile(filePath, description) {
  const exists = fs.existsSync(filePath);
  console.log(`   ${exists ? '✅' : '❌'} ${description}: ${filePath}`);
  return exists;
}

function checkDirectory(dirPath, description) {
  const exists = fs.existsSync(dirPath) && fs.statSync(dirPath).isDirectory();
  console.log(`   ${exists ? '✅' : '❌'} ${description}: ${dirPath}`);
  return exists;
}

async function checkFrontend() {
  console.log('🧪 Vérification du frontend REMOTE...');
  console.log('=' .repeat(50));
  
  let allGood = true;
  
  // Test 1: Fichiers principaux
  console.log('\n1. Fichiers principaux...');
  allGood &= checkFile('package.json', 'Package.json');
  allGood &= checkFile('vite.config.js', 'Config Vite');
  allGood &= checkFile('index.html', 'HTML principal');
  allGood &= checkFile('.env', 'Variables environnement');
  
  // Test 2: Structure src
  console.log('\n2. Structure src...');
  allGood &= checkFile('src/index.jsx', 'Point d\'entrée');
  allGood &= checkFile('src/App.jsx', 'Composant App');
  allGood &= checkDirectory('src/components', 'Dossier composants');
  allGood &= checkDirectory('src/stores', 'Dossier stores');
  allGood &= checkDirectory('src/services', 'Dossier services');
  allGood &= checkDirectory('src/styles', 'Dossier styles');
  
  // Test 3: Composants clés
  console.log('\n3. Composants clés...');
  allGood &= checkFile('src/components/Game/GameInterface.jsx', 'GameInterface');
  allGood &= checkFile('src/components/UI/LoadingSpinner.jsx', 'LoadingSpinner');
  allGood &= checkFile('src/components/UI/ErrorBoundary.jsx', 'ErrorBoundary');
  
  // Test 4: Services
  console.log('\n4. Services...');
  allGood &= checkFile('src/services/websocketService.js', 'WebSocket Service');
  allGood &= checkFile('src/services/audioService.js', 'Audio Service');
  
  // Test 5: Stores
  console.log('\n5. Stores Zustand...');
  allGood &= checkFile('src/stores/gameStore.js', 'Game Store');
  allGood &= checkFile('src/stores/osStore.js', 'OS Store');
  allGood &= checkFile('src/stores/tomStore.js', 'Tom Store');
  
  // Test 6: Styles
  console.log('\n6. Styles...');
  allGood &= checkFile('src/styles/index.css', 'CSS principal');
  allGood &= checkFile('src/styles/app.css', 'CSS app');
  
  // Test 7: Dependencies
  console.log('\n7. Dépendances...');
  allGood &= checkDirectory('node_modules', 'Node modules');
  
  if (fs.existsSync('package.json')) {
    try {
      const pkg = JSON.parse(fs.readFileSync('package.json', 'utf8'));
      const requiredDeps = [
        'react', 'react-dom', 'zustand', 'framer-motion', 
        'howler', 'uuid', 'react-draggable', 'react-resizable'
      ];
      
      console.log('   Vérification des dépendances requises:');
      for (const dep of requiredDeps) {
        const exists = pkg.dependencies && pkg.dependencies[dep];
        console.log(`     ${exists ? '✅' : '❌'} ${dep}`);
        if (!exists) allGood = false;
      }
    } catch (e) {
      console.log('   ❌ Erreur lecture package.json');
      allGood = false;
    }
  }
  
  // Test 8: Configuration
  console.log('\n8. Configuration...');
  if (fs.existsSync('.env')) {
    try {
      const envContent = fs.readFileSync('.env', 'utf8');
      const hasWsUrl = envContent.includes('VITE_WS_URL');
      const hasApiUrl = envContent.includes('VITE_API_URL');
      
      console.log(`   ${hasWsUrl ? '✅' : '❌'} VITE_WS_URL configuré`);
      console.log(`   ${hasApiUrl ? '✅' : '❌'} VITE_API_URL configuré`);
      
      if (!hasWsUrl || !hasApiUrl) allGood = false;
    } catch (e) {
      console.log('   ❌ Erreur lecture .env');
      allGood = false;
    }
  }
  
  console.log('\n' + '='.repeat(50));
  
  if (allGood) {
    console.log('🎉 Frontend correctement configuré !');
    console.log('\n💡 Pour lancer le dev server:');
    console.log('   npm run dev');
  } else {
    console.log('❌ Des problèmes ont été détectés');
    console.log('\n💡 Corrections suggérées:');
    if (!fs.existsSync('node_modules')) {
      console.log('   - Installer les dépendances: npm install');
    }
    console.log('   - Vérifier les fichiers manquants ci-dessus');
    console.log('   - Vérifier la configuration .env');
  }
  
  return allGood;
}

// Exécuter la vérification
if (require.main === module) {
  checkFrontend().then(success => {
    process.exit(success ? 0 : 1);
  }).catch(error => {
    console.error('❌ Erreur fatale:', error);
    process.exit(1);
  });
}

module.exports = { checkFrontend };
