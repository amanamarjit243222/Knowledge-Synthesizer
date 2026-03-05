import { INITIAL_STATE } from './config.js';
import { GraphRenderer } from './graph/renderer.js';
import { UIManager } from './ui/interface.js';
import { NavigationController } from './ui/navigation.js';
import { APIClient } from './api/client.js';

class KnowledgeSynthesizerApp {
    constructor() {
        window.appState = { ...INITIAL_STATE };
        this.graphRenderer = new GraphRenderer('knowledgeGraph');
        this.uiManager = new UIManager(window.appState, this.graphRenderer);
        this.navigation = new NavigationController(this.graphRenderer);
        this.apiClient = new APIClient(window.appState, this.uiManager);
    }

    init() {
        this.uiManager.removePreloader();
        this.bindEvents();
    }

    bindEvents() {
        // Theme
        const themeBtn = document.getElementById('themeToggleBtn');
        if (themeBtn) themeBtn.onclick = () => this.uiManager.toggleTheme();

        // Navigation
        window.navigateTo = (id) => this.navigation.navigateTo(id);

        // Input Options
        document.querySelectorAll('.input-group .option').forEach(opt => {
            opt.onclick = (e) => this.uiManager.selectOption(e.currentTarget, 'inputType', e.currentTarget.dataset.value);
        });

        document.querySelectorAll('.disc-group .option').forEach(opt => {
            opt.onclick = (e) => this.uiManager.selectOption(e.currentTarget, 'discType', e.currentTarget.dataset.value);
        });

        // File/Upload Area
        const uploadArea = document.getElementById('uploadArea');
        if (uploadArea) {
            uploadArea.onclick = () => {
                if (window.appState.inputType === 'live') {
                    window.appState.isRecording = !window.appState.isRecording;
                    uploadArea.classList.toggle('recording', window.appState.isRecording);
                    document.getElementById('uploadText').innerText = window.appState.isRecording ?
                        "Recording in progress... (Click to Stop)" : "Recording stopped. Ready to Execute.";
                } else if (window.appState.inputType === 'file') {
                    document.getElementById('fileInput').click();
                }
            };
        }

        const fileInput = document.getElementById('fileInput');
        if (fileInput) {
            fileInput.onchange = (e) => this.uiManager.handleFileSelect(e.target);
        }

        // Processing
        const processBtn = document.getElementById('processBtn');
        if (processBtn) {
            processBtn.onclick = () => this.apiClient.startProcessing(id => this.navigation.navigateTo(id));
        }
    }
}

const App = new KnowledgeSynthesizerApp();
window.onload = () => App.init();
