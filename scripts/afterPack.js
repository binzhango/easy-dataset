#!/usr/bin/env node

/**
 * Electron Builder afterPack hook
 * 
 * This script runs after the app is packed but before creating installers.
 * It handles platform-specific Python bundling.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

module.exports = async function(context) {
  const { electronPlatformName, appOutDir } = context;
  
  console.log(`\n=== Running afterPack for ${electronPlatformName} ===\n`);
  
  // Determine Python backend location in the packaged app
  let resourcesPath;
  if (electronPlatformName === 'darwin') {
    resourcesPath = path.join(appOutDir, 'Easy Dataset.app', 'Contents', 'Resources');
  } else if (electronPlatformName === 'win32') {
    resourcesPath = path.join(appOutDir, 'resources');
  } else if (electronPlatformName === 'linux') {
    resourcesPath = path.join(appOutDir, 'resources');
  }
  
  const pythonBackendDest = path.join(resourcesPath, 'python-backend');
  
  console.log(`Python backend location: ${pythonBackendDest}`);
  
  // Verify Python backend was copied
  if (!fs.existsSync(pythonBackendDest)) {
    console.error('✗ Python backend not found in packaged app!');
    throw new Error('Python backend missing from package');
  }
  
  console.log('✓ Python backend found in package');
  
  // Create a marker file to indicate this is a production build
  const markerFile = path.join(pythonBackendDest, '.production');
  fs.writeFileSync(markerFile, new Date().toISOString());
  console.log('✓ Created production marker file');
  
  // Platform-specific post-processing
  if (electronPlatformName === 'darwin') {
    console.log('Processing macOS bundle...');
    // Add any macOS-specific processing here
  } else if (electronPlatformName === 'win32') {
    console.log('Processing Windows bundle...');
    // Add any Windows-specific processing here
  } else if (electronPlatformName === 'linux') {
    console.log('Processing Linux bundle...');
    // Add any Linux-specific processing here
  }
  
  console.log('\n=== afterPack completed successfully ===\n');
};
