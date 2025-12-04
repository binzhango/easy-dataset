const { ipcMain } = require('electron');
const { checkUpdate, downloadUpdate, installUpdate } = require('./updater');
const { checkForBackendUpdates, handleBackendUpdate } = require('./python-updater');

/**
 * 设置 IPC 处理程序
 * @param {Object} app Electron app 对象
 * @param {boolean} isDev 是否为开发环境
 */
function setupIpcHandlers(app, isDev) {
  // 获取用户数据路径
  ipcMain.on('get-user-data-path', event => {
    event.returnValue = app.getPath('userData');
  });

  // 检查更新 (Electron app)
  ipcMain.handle('check-update', async () => {
    return await checkUpdate(isDev);
  });

  // 下载更新 (Electron app)
  ipcMain.handle('download-update', async () => {
    return await downloadUpdate();
  });

  // 安装更新 (Electron app)
  ipcMain.handle('install-update', () => {
    return installUpdate();
  });

  // 检查 Python 后端更新
  ipcMain.handle('check-backend-update', async (event, currentVersion, port = 1717) => {
    try {
      return await checkForBackendUpdates(currentVersion, port);
    } catch (error) {
      console.error('Failed to check backend updates:', error);
      return null;
    }
  });

  // 处理 Python 后端更新（完整流程）
  ipcMain.handle('handle-backend-update', async (event, currentVersion, port = 1717) => {
    try {
      const { BrowserWindow } = require('electron');
      const mainWindow = BrowserWindow.getFocusedWindow();
      await handleBackendUpdate(currentVersion, mainWindow, port);
      return { success: true };
    } catch (error) {
      console.error('Failed to handle backend update:', error);
      return { success: false, error: error.message };
    }
  });
}

module.exports = {
  setupIpcHandlers
};
