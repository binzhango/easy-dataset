const { dialog } = require('electron');
const http = require('http');

/**
 * Check for Python backend updates
 * @param {string} currentVersion Current backend version
 * @param {number} port Backend server port
 * @returns {Promise<Object|null>} Update information or null
 */
async function checkForBackendUpdates(currentVersion, port = 1717) {
  try {
    console.log(`Checking for Python backend updates (current: ${currentVersion})`);

    const response = await makeRequest(
      `http://localhost:${port}/api/updates/check?current_version=${currentVersion}`,
      'GET'
    );

    if (response.update_available) {
      console.log(`Update available: ${response.latest_version}`);
      return response;
    } else {
      console.log('No updates available');
      return null;
    }
  } catch (error) {
    console.error('Failed to check for backend updates:', error);
    return null;
  }
}

/**
 * Download a backend update
 * @param {string} downloadUrl URL to download from
 * @param {number} port Backend server port
 * @returns {Promise<Object>} Download result
 */
async function downloadBackendUpdate(downloadUrl, port = 1717) {
  try {
    console.log(`Downloading backend update from ${downloadUrl}`);

    const response = await makeRequest(
      `http://localhost:${port}/api/updates/download`,
      'POST',
      { download_url: downloadUrl }
    );

    if (response.success) {
      console.log(`Update downloaded to ${response.file_path}`);
    } else {
      console.error('Failed to download update:', response.message);
    }

    return response;
  } catch (error) {
    console.error('Failed to download backend update:', error);
    throw error;
  }
}

/**
 * Install a backend update
 * @param {string} updateFile Path to update file
 * @param {number} port Backend server port
 * @returns {Promise<Object>} Installation result
 */
async function installBackendUpdate(updateFile, port = 1717) {
  try {
    console.log(`Installing backend update from ${updateFile}`);

    const response = await makeRequest(
      `http://localhost:${port}/api/updates/install`,
      'POST',
      { update_file: updateFile }
    );

    if (response.success) {
      console.log('Update installed successfully');
    } else {
      console.error('Failed to install update:', response.message);
    }

    return response;
  } catch (error) {
    console.error('Failed to install backend update:', error);
    throw error;
  }
}

/**
 * Prompt user to install update
 * @param {Object} updateInfo Update information
 * @param {Object} mainWindow Main window
 * @returns {Promise<boolean>} Whether user wants to install
 */
async function promptForUpdate(updateInfo, mainWindow) {
  const result = await dialog.showMessageBox(mainWindow, {
    type: 'info',
    title: 'Update Available',
    message: `A new version of Easy Dataset is available!`,
    detail: `Current version: ${updateInfo.current_version}\nNew version: ${updateInfo.latest_version}\n\n${updateInfo.release_notes || 'No release notes available.'}`,
    buttons: ['Download and Install', 'Later'],
    defaultId: 0,
    cancelId: 1,
  });

  return result.response === 0;
}

/**
 * Show update progress
 * @param {Object} mainWindow Main window
 * @param {string} message Progress message
 */
function showUpdateProgress(mainWindow, message) {
  // Send progress to renderer process
  if (mainWindow && mainWindow.webContents) {
    mainWindow.webContents.send('update-progress', message);
  }
  console.log(`Update progress: ${message}`);
}

/**
 * Handle the complete update process
 * @param {string} currentVersion Current backend version
 * @param {Object} mainWindow Main window
 * @param {number} port Backend server port
 */
async function handleBackendUpdate(currentVersion, mainWindow, port = 1717) {
  try {
    // Check for updates
    const updateInfo = await checkForBackendUpdates(currentVersion, port);

    if (!updateInfo) {
      return; // No updates available
    }

    // Prompt user
    const shouldUpdate = await promptForUpdate(updateInfo, mainWindow);

    if (!shouldUpdate) {
      return; // User declined
    }

    // Download update
    showUpdateProgress(mainWindow, 'Downloading update...');
    const downloadResult = await downloadBackendUpdate(updateInfo.download_url, port);

    if (!downloadResult.success) {
      dialog.showErrorBox('Update Failed', 'Failed to download update. Please try again later.');
      return;
    }

    // Install update
    showUpdateProgress(mainWindow, 'Installing update...');
    const installResult = await installBackendUpdate(downloadResult.file_path, port);

    if (!installResult.success) {
      dialog.showErrorBox('Update Failed', 'Failed to install update. Please try again later.');
      return;
    }

    // Prompt to restart
    const restartResult = await dialog.showMessageBox(mainWindow, {
      type: 'info',
      title: 'Update Installed',
      message: 'Update installed successfully!',
      detail: 'The application needs to restart to apply the update.',
      buttons: ['Restart Now', 'Restart Later'],
      defaultId: 0,
    });

    if (restartResult.response === 0) {
      const { app } = require('electron');
      app.relaunch();
      app.quit();
    }
  } catch (error) {
    console.error('Error during update process:', error);
    dialog.showErrorBox('Update Error', `An error occurred during the update process: ${error.message}`);
  }
}

/**
 * Make HTTP request to backend
 * @param {string} url Request URL
 * @param {string} method HTTP method
 * @param {Object} data Request body
 * @returns {Promise<Object>} Response data
 */
function makeRequest(url, method = 'GET', data = null) {
  return new Promise((resolve, reject) => {
    const urlObj = new URL(url);
    const options = {
      hostname: urlObj.hostname,
      port: urlObj.port,
      path: urlObj.pathname + urlObj.search,
      method: method,
      headers: {
        'Content-Type': 'application/json',
      },
    };

    const req = http.request(options, res => {
      let body = '';

      res.on('data', chunk => {
        body += chunk;
      });

      res.on('end', () => {
        try {
          const response = JSON.parse(body);
          resolve(response);
        } catch (error) {
          reject(new Error(`Failed to parse response: ${error.message}`));
        }
      });
    });

    req.on('error', error => {
      reject(error);
    });

    if (data) {
      req.write(JSON.stringify(data));
    }

    req.end();
  });
}

module.exports = {
  checkForBackendUpdates,
  downloadBackendUpdate,
  installBackendUpdate,
  promptForUpdate,
  showUpdateProgress,
  handleBackendUpdate,
};
