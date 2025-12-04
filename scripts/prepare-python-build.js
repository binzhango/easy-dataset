#!/usr/bin/env node

/**
 * Prepare Python backend for Electron build
 * 
 * This script:
 * 1. Installs Python dependencies
 * 2. Creates a requirements.txt if needed
 * 3. Validates Python installation
 * 4. Prepares the backend for bundling
 */

const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

const PYTHON_BACKEND_DIR = path.join(__dirname, '..', 'python-backend');
const REQUIREMENTS_FILE = path.join(PYTHON_BACKEND_DIR, 'requirements.txt');

console.log('=== Preparing Python Backend for Build ===\n');

// Check if Python is installed
function checkPython() {
  console.log('Checking Python installation...');
  try {
    const version = execSync('python3 --version', { encoding: 'utf-8' }).trim();
    console.log(`✓ Found ${version}`);
    return 'python3';
  } catch (error) {
    try {
      const version = execSync('python --version', { encoding: 'utf-8' }).trim();
      console.log(`✓ Found ${version}`);
      return 'python';
    } catch (error) {
      console.error('✗ Python not found. Please install Python 3.9 or higher.');
      process.exit(1);
    }
  }
}

// Check if requirements.txt exists
function checkRequirements() {
  console.log('\nChecking requirements.txt...');
  if (!fs.existsSync(REQUIREMENTS_FILE)) {
    console.error(`✗ requirements.txt not found at ${REQUIREMENTS_FILE}`);
    process.exit(1);
  }
  console.log('✓ requirements.txt found');
}

// Install Python dependencies
function installDependencies(pythonCmd) {
  console.log('\nInstalling Python dependencies...');
  console.log('This may take a few minutes...\n');
  
  try {
    // Install the package in editable mode
    execSync(`${pythonCmd} -m pip install -e "${PYTHON_BACKEND_DIR}"`, {
      stdio: 'inherit',
      cwd: PYTHON_BACKEND_DIR
    });
    console.log('\n✓ Python dependencies installed successfully');
  } catch (error) {
    console.error('\n✗ Failed to install Python dependencies');
    console.error('Please run manually: pip install -e python-backend');
    process.exit(1);
  }
}

// Verify installation
function verifyInstallation(pythonCmd) {
  console.log('\nVerifying installation...');
  
  try {
    // Check if easy_dataset can be imported
    execSync(
      `${pythonCmd} -c "import easy_dataset; import easy_dataset_server; print('OK')"`,
      { encoding: 'utf-8', cwd: PYTHON_BACKEND_DIR }
    );
    console.log('✓ Python backend is properly installed');
  } catch (error) {
    console.error('✗ Failed to import Python backend modules');
    console.error('Please check your Python installation');
    process.exit(1);
  }
}

// Clean up build artifacts
function cleanBuildArtifacts() {
  console.log('\nCleaning build artifacts...');
  
  const dirsToClean = [
    path.join(PYTHON_BACKEND_DIR, '__pycache__'),
    path.join(PYTHON_BACKEND_DIR, '.pytest_cache'),
    path.join(PYTHON_BACKEND_DIR, 'htmlcov'),
    path.join(PYTHON_BACKEND_DIR, 'dist'),
    path.join(PYTHON_BACKEND_DIR, 'build'),
  ];
  
  dirsToClean.forEach(dir => {
    if (fs.existsSync(dir)) {
      fs.rmSync(dir, { recursive: true, force: true });
      console.log(`  Removed ${path.basename(dir)}`);
    }
  });
  
  // Remove .pyc files
  try {
    if (process.platform === 'win32') {
      execSync(`del /s /q "${PYTHON_BACKEND_DIR}\\*.pyc" 2>nul`, { stdio: 'ignore' });
    } else {
      execSync(`find "${PYTHON_BACKEND_DIR}" -name "*.pyc" -delete`, { stdio: 'ignore' });
    }
    console.log('  Removed .pyc files');
  } catch (error) {
    // Ignore errors
  }
  
  console.log('✓ Build artifacts cleaned');
}

// Main execution
function main() {
  try {
    const pythonCmd = checkPython();
    checkRequirements();
    cleanBuildArtifacts();
    installDependencies(pythonCmd);
    verifyInstallation(pythonCmd);
    
    console.log('\n=== Python Backend Ready for Build ===\n');
    console.log('You can now run:');
    console.log('  npm run electron-build-mac    (for macOS)');
    console.log('  npm run electron-build-win    (for Windows)');
    console.log('  npm run electron-build-linux  (for Linux)');
    console.log('  npm run electron-build        (for all platforms)\n');
  } catch (error) {
    console.error('\n✗ Build preparation failed:', error.message);
    process.exit(1);
  }
}

main();
