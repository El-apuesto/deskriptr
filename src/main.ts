import { app, BrowserWindow, ipcMain, dialog, shell, Menu } from 'electron';
import path from 'path';
import { spawn } from 'child_process';
import Store from 'electron-store';
import { AppState, UsageStats, License, TranscriptionResult } from './types/index.js';

const __filename = __filename || '';
const __dirname = path.dirname(__filename) || __dirname;

// Handle Squirrel.Windows installer events
if (process.platform === 'win32') {
  const squirrelCommand = process.argv[1];
  if (squirrelCommand === '--squirrel-install' || squirrelCommand === '--squirrel-updated') {
    // Install desktop and start menu shortcuts
    app.quit();
  } else if (squirrelCommand === '--squirrel-uninstall') {
    // Remove shortcuts
    app.quit();
  } else if (squirrelCommand === '--squirrel-obsolete') {
    app.quit();
  }
}

class TattletaleApp {
  private mainWindow: BrowserWindow | null = null;
  private store: Store;
  private transcriptionProcess: any = null;

  constructor() {
    this.store = new Store();
    this.initializeApp();
  }

  private async initializeApp() {
    await app.whenReady();
    
    // Set up menu
    this.createMenu();
    
    // Create main window
    await this.createMainWindow();
    
    // Set up IPC handlers
    this.setupIpcHandlers();
    
    // Handle app events
    this.setupAppEvents();
  }

  private async createMainWindow() {
    this.mainWindow = new BrowserWindow({
      width: 1200,
      height: 800,
      minWidth: 1000,
      minHeight: 600,
      webPreferences: {
        nodeIntegration: false,
        contextIsolation: true,
        enableRemoteModule: false,
        preload: path.join(__dirname, 'preload.js'),
      },
      icon: path.join(__dirname, '../assets/icon.png'),
      show: false,
      titleBarStyle: process.platform === 'darwin' ? 'hiddenInset' : 'default',
    });

    // Load the app
    const isDev = process.env.NODE_ENV === 'development';
    if (isDev) {
      this.mainWindow.loadURL('http://localhost:3000');
      this.mainWindow.webContents.openDevTools();
    } else {
      this.mainWindow.loadFile(path.join(__dirname, '../dist/renderer/index.html'));
    }

    this.mainWindow.once('ready-to-show', () => {
      this.mainWindow?.show();
    });

    this.mainWindow.on('closed', () => {
      this.mainWindow = null;
    });
  }

  private createMenu() {
    const template = [
      {
        label: 'Tattletale',
        submenu: [
          {
            label: 'About Tattletale',
            click: () => {
              this.showAboutDialog();
            }
          },
          { type: 'separator' },
          {
            label: 'Settings',
            accelerator: 'CmdOrCtrl+,',
            click: () => {
              this.mainWindow?.webContents.send('show-settings');
            }
          },
          { type: 'separator' },
          {
            role: 'hide'
          },
          {
            role: 'hideothers'
          },
          {
            role: 'unhide'
          },
          { type: 'separator' },
          {
            role: 'quit'
          }
        ]
      },
      {
        label: 'File',
        submenu: [
          {
            label: 'New Transcription',
            accelerator: 'CmdOrCtrl+N',
            click: () => {
              this.mainWindow?.webContents.send('new-transcription');
            }
          },
          {
            label: 'Open File...',
            accelerator: 'CmdOrCtrl+O',
            click: async () => {
              const result = await dialog.showOpenDialog(this.mainWindow!, {
                properties: ['openFile'],
                filters: [
                  {
                    name: 'Audio/Video Files',
                    extensions: ['mp3', 'mp4', 'wav', 'm4a', 'mov', 'webm']
                  }
                ]
              });
              if (!result.canceled && result.filePaths.length > 0) {
                this.mainWindow?.webContents.send('file-selected', result.filePaths[0]);
              }
            }
          },
          { type: 'separator' },
          {
            role: 'close'
          }
        ]
      },
      {
        label: 'Edit',
        submenu: [
          {
            role: 'undo'
          },
          {
            role: 'redo'
          },
          {
            type: 'separator'
          },
          {
            role: 'cut'
          },
          {
            role: 'copy'
          },
          {
            role: 'paste'
          },
          {
            role: 'selectall'
          }
        ]
      },
      {
        label: 'View',
        submenu: [
          {
            role: 'reload'
          },
          {
            role: 'forceReload'
          },
          {
            role: 'toggleDevTools'
          },
          {
            type: 'separator'
          },
          {
            role: 'resetZoom'
          },
          {
            role: 'zoomIn'
          },
          {
            role: 'zoomOut'
          },
          {
            type: 'separator'
          },
          {
            role: 'togglefullscreen'
          }
        ]
      },
      {
        label: 'Window',
        submenu: [
          {
            role: 'minimize'
          },
          {
            role: 'close'
          }
        ]
      },
      {
        label: 'Help',
        submenu: [
          {
            label: 'Learn More',
            click: () => {
              shell.openExternal('https://tattletale.app');
            }
          }
        ]
      }
    ];

    const menu = Menu.buildFromTemplate(template as any);
    Menu.setApplicationMenu(menu);
  }

  private showAboutDialog() {
    dialog.showMessageBox(this.mainWindow!, {
      type: 'info',
      title: 'About Tattletale',
      message: 'Tattletale',
      detail: 'Privacy-first desktop transcription app using Whisper AI\n\nVersion 1.0.0',
      buttons: ['OK']
    });
  }

  private setupIpcHandlers() {
    // Get app state
    ipcMain.handle('get-app-state', () => {
      return this.getAppState();
    });

    // Update usage
    ipcMain.handle('update-usage', (event, minutes: number) => {
      return this.updateUsage(minutes);
    });

    // Validate license
    ipcMain.handle('validate-license', async (event, licenseKey: string) => {
      return this.validateLicense(licenseKey);
    });

    // Get stored license
    ipcMain.handle('get-license', () => {
      return this.store.get('license') as License | null;
    });

    // Store license
    ipcMain.handle('store-license', (event, license: License) => {
      this.store.set('license', license);
      return true;
    });

    // Clear license
    ipcMain.handle('clear-license', () => {
      this.store.delete('license');
      return true;
    });

    // Select file
    ipcMain.handle('select-file', async () => {
      const result = await dialog.showOpenDialog(this.mainWindow!, {
        properties: ['openFile'],
        filters: [
          {
            name: 'Audio/Video Files',
            extensions: ['mp3', 'mp4', 'wav', 'm4a', 'mov', 'webm']
          }
        ]
      });
      
      if (!result.canceled && result.filePaths.length > 0) {
        return result.filePaths[0];
      }
      return null;
    });

    // Start transcription
    ipcMain.handle('start-transcription', async (event, filePath: string) => {
      return this.startTranscription(filePath);
    });

    // Cancel transcription
    ipcMain.handle('cancel-transcription', () => {
      if (this.transcriptionProcess) {
        this.transcriptionProcess.kill();
        this.transcriptionProcess = null;
      }
      return true;
    });

    // Export transcript
    ipcMain.handle('export-transcript', async (event, data: { format: string; content: string; filename: string }) => {
      return this.exportTranscript(data.format, data.content, data.filename);
    });

    // Open external link
    ipcMain.handle('open-external', async (event, url: string) => {
      await shell.openExternal(url);
      return true;
    });

    // Show message box
    ipcMain.handle('show-message', async (event, options: any) => {
      const result = await dialog.showMessageBox(this.mainWindow!, options);
      return result;
    });
  }

  private setupAppEvents() {
    app.on('window-all-closed', () => {
      if (process.platform !== 'darwin') {
        app.quit();
      }
    });

    app.on('activate', async () => {
      if (BrowserWindow.getAllWindows().length === 0) {
        await this.createMainWindow();
      }
    });

    app.on('before-quit', () => {
      if (this.transcriptionProcess) {
        this.transcriptionProcess.kill();
      }
    });
  }

  private getAppState(): AppState {
    const usage = this.store.get('usage', {
      minutesUsed: 0,
      lastResetDate: new Date().toISOString(),
      nextResetDate: this.getNextMonthDate().toISOString()
    }) as UsageStats;

    const license = this.store.get('license') as License | null;
    
    // Check if usage should be reset
    const now = new Date();
    const nextReset = new Date(usage.nextResetDate);
    if (now >= nextReset) {
      usage.minutesUsed = 0;
      usage.lastResetDate = now.toISOString();
      usage.nextResetDate = this.getNextMonthDate().toISOString();
      this.store.set('usage', usage);
    }

    return {
      currentTier: license?.tier || 'free',
      usage,
      license,
      currentTranscript: null,
      isTranscribing: false,
      transcriptionProgress: 0
    };
  }

  private updateUsage(minutes: number): boolean {
    const usage = this.store.get('usage', {
      minutesUsed: 0,
      lastResetDate: new Date().toISOString(),
      nextResetDate: this.getNextMonthDate().toISOString()
    }) as UsageStats;

    const license = this.store.get('license') as License | null;
    
    // Unlimited tiers don't have usage limits
    if (license?.tier === 'unlimited' || license?.tier === 'student') {
      return true;
    }

    // Check if usage should be reset
    const now = new Date();
    const nextReset = new Date(usage.nextResetDate);
    if (now >= nextReset) {
      usage.minutesUsed = 0;
      usage.lastResetDate = now.toISOString();
      usage.nextResetDate = this.getNextMonthDate().toISOString();
    }

    // Check if user has enough minutes
    if (usage.minutesUsed + minutes > 60) {
      return false;
    }

    usage.minutesUsed += minutes;
    this.store.set('usage', usage);
    return true;
  }

  private async validateLicense(licenseKey: string): Promise<License | null> {
    // In a real app, this would call your backend API
    // For demo purposes, we'll simulate validation
    
    // Mock validation logic
    if (licenseKey.startsWith('UNLIMITED-')) {
      return {
        key: licenseKey,
        tier: 'unlimited',
        status: 'active'
      };
    } else if (licenseKey.startsWith('STUDENT-')) {
      return {
        key: licenseKey,
        tier: 'student',
        status: 'active',
        isStudent: true,
        expiryDate: this.getSixMonthsFromNow().toISOString()
      };
    }
    
    return null;
  }

  private async startTranscription(filePath: string): Promise<boolean> {
    try {
      // Read the audio file
      const fs = await import('fs/promises');
      const audioBuffer = await fs.readFile(filePath);
      
      // Get file info
      const stats = await fs.stat(filePath);
      const fileSizeInMB = stats.size / (1024 * 1024);
      
      // Simulate transcription with progress updates
      // In a real implementation, you would:
      // 1. Decode the audio file to raw samples
      // 2. Pass it to the Whisper service
      // 3. Process the results
      
      return new Promise((resolve) => {
        let progress = 0;
        const interval = setInterval(() => {
          progress += Math.random() * 8 + 2; // Random progress between 2-10%
          progress = Math.min(progress, 100);
          
          this.mainWindow?.webContents.send('transcription-progress', Math.round(progress));
          
          if (progress >= 100) {
            clearInterval(interval);
            
            // Simulate transcription result based on file size
            const segmentCount = Math.max(2, Math.min(8, Math.floor(fileSizeInMB / 5)));
            const segments: any[] = [];
            
            for (let i = 0; i < segmentCount; i++) {
              const startTime = i * 8;
              const duration = 3 + Math.random() * 4;
              
              const sampleTexts = [
                'Welcome to this transcription example. This demonstrates how Tattletale processes audio files.',
                'The Whisper AI model provides highly accurate speech recognition with speaker detection.',
                'All processing happens locally on your device, ensuring complete privacy and security.',
                'You can edit the transcript directly in the interface and export to multiple formats.',
                'Speaker changes are detected automatically based on pauses in the conversation.',
                'Thank you for using Tattletale for your transcription needs.',
                'This is a sample transcription to demonstrate the app functionality.',
                'Upgrade to unlock unlimited transcription and additional export formats.'
              ];
              
              segments.push({
                timestamp: this.formatTimestamp(startTime),
                speaker: `Speaker ${(i % 3) + 1}`,
                text: sampleTexts[i % sampleTexts.length],
                startTime: startTime,
                endTime: startTime + duration
              });
            }
            
            const mockResult: TranscriptionResult = {
              segments,
              totalDuration: segmentCount * 8,
              speakers: Math.min(3, segmentCount)
            };
            
            this.mainWindow?.webContents.send('transcription-complete', mockResult);
            resolve(true);
          }
        }, 300);
      });
    } catch (error) {
      console.error('Transcription failed:', error);
      throw error;
    }
  }

  private formatTimestamp(seconds: number): string {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = Math.floor(seconds % 60);
    
    if (hours > 0) {
      return `[${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}]`;
    } else {
      return `[${minutes}:${secs.toString().padStart(2, '0')}]`;
    }
  }

  private async exportTranscript(format: string, content: string, filename: string): Promise<boolean> {
    try {
      const result = await dialog.showSaveDialog(this.mainWindow!, {
        defaultPath: filename,
        filters: this.getFileFilters(format)
      });
      
      if (!result.canceled && result.filePath) {
        const fs = await import('fs/promises');
        await fs.writeFile(result.filePath, content, 'utf8');
        return true;
      }
      return false;
    } catch (error) {
      console.error('Export error:', error);
      return false;
    }
  }

  private getFileFilters(format: string) {
    switch (format) {
      case 'txt':
        return [{ name: 'Text Files', extensions: ['txt'] }];
      case 'srt':
        return [{ name: 'Subtitle Files', extensions: ['srt'] }];
      case 'pdf':
        return [{ name: 'PDF Files', extensions: ['pdf'] }];
      case 'docx':
        return [{ name: 'Word Documents', extensions: ['docx'] }];
      default:
        return [{ name: 'All Files', extensions: ['*'] }];
    }
  }

  private getNextMonthDate(): Date {
    const date = new Date();
    date.setMonth(date.getMonth() + 1);
    date.setDate(1);
    return date;
  }

  private getSixMonthsFromNow(): Date {
    const date = new Date();
    date.setMonth(date.getMonth() + 6);
    return date;
  }
}

// Initialize the app
new TattletaleApp();