/* --- APP STATE & API CONFIG --- */
const APP_CONFIG = {
    apiEndpoint: "http://localhost:8000/synthesize", // Placeholder for your backend
    mockDelay: 0 // Simulate processing time (Increased for effect)
};

let appState = {
    inputType: 'live', // live, text, file
    discType: 'roundtable',
    selectedFile: null,
    isRecording: false,
    graphData: { nodes: [], edges: [] },
    analysisResult: null
};

/* --- PRELOADER LOGIC --- */
function removePreloader() {
    const preloader = document.getElementById('initial-preloader');
    if (preloader && !preloader.classList.contains('loaded')) {
        // Simulate a brief "boot up" sequence
        setTimeout(() => {
            preloader.classList.add('loaded');
        }, 1500);
    }
}

// Check if page is already loaded
if (document.readyState === 'complete') {
    removePreloader();
} else {
    window.addEventListener('load', removePreloader);
}

// Safety fallback: force remove after 5 seconds max if window.load hangs (e.g. missing images)
setTimeout(() => {
    removePreloader();
}, 5000);

/* --- THEME & UI SETUP --- */
// Default to Dark Mode for Deeptech aesthetic
let isDark = true;

function toggleTheme() {
    isDark = !isDark;
    const body = document.body;

    // --- MODIFIED: IMAGE SWITCHING LOGIC (Cleaned up) ---
    const btnImg = document.getElementById('themeBtnImg');
    if (btnImg) {
        // Switches between 'team_symbol_light.png' and 'team_symbol_dark.png' inside the button
        // In Dark mode, we usually want the "Light Mode" icon (sun) or the specific dark theme asset
        // Assuming team_symbol_light.png is for Light Mode and team_symbol_dark.png is for Dark Mode
        btnImg.src = isDark ? 'team_symbol_dark.png' : 'team_symbol_light.png';
    }

    if (isDark) body.setAttribute('data-theme', 'dark');
    else body.removeAttribute('data-theme');

    // Check if data exists and canvas is accessible before redrawing
    if (appState.graphData.nodes.length > 0 && document.getElementById('knowledgeGraph')) {
        drawGraph();
    }
}

/* --- NAVIGATION --- */
const main = document.getElementById('mainContainer');

function navigateTo(targetId) {
    if (document.getElementById(targetId).classList.contains('is-active')) return;

    // Fold Transition
    main.classList.remove('animating');
    main.classList.add('folded');

    setTimeout(() => {
        main.classList.add('fly-out');
        setTimeout(() => {
            document.querySelectorAll('.page-view').forEach(v => v.classList.remove('is-active'));
            const nextView = document.getElementById(targetId);
            nextView.classList.add('is-active');

            main.classList.remove('fly-out');
            main.classList.add('fly-in-start');
            void main.offsetWidth; // Force Reflow
            main.classList.add('animating');
            main.classList.remove('fly-in-start');

            setTimeout(() => {
                main.classList.remove('folded');
                if (targetId === 'result-view') setTimeout(initGraph, 300);
            }, 600);
        }, 500);
    }, 600);
}

/* --- INPUT HANDLING --- */
function selectOption(el, group, value) {
    // Update UI
    Array.from(el.parentElement.children).forEach(c => c.classList.remove('selected'));
    el.classList.add('selected');

    // Update State
    appState[group] = value;

    // Reset Recording State on switch
    appState.isRecording = false;
    document.getElementById('uploadArea').classList.remove('recording');

    // Specific Logic for Input Type
    if (group === 'inputType') {
        const area = document.getElementById('uploadArea');
        const textSpan = document.getElementById('uploadText');

        // Clear previous contents (image preview or textarea)
        const existingPreview = area.querySelector('.preview');
        if (existingPreview) existingPreview.remove();

        const existingTextarea = area.querySelector('textarea');
        if (existingTextarea) existingTextarea.remove();

        // Reset Text visibility
        textSpan.style.display = 'block';

        if (value === 'live') {
            textSpan.innerText = 'Click to Activate Microphone...';
            area.style.pointerEvents = 'all';
        } else if (value === 'text') {
            // Inject Text Area for UX consistency
            textSpan.style.display = 'none';
            const textarea = document.createElement('textarea');
            textarea.placeholder = "Paste your raw data (transcript) here...";
            textarea.onclick = (e) => e.stopPropagation(); // Prevent parent click
            area.appendChild(textarea);
            area.style.pointerEvents = 'all';
        } else {
            textSpan.innerText = 'Click or Drop file here...';
            area.style.pointerEvents = 'all';
        }
    }
}

function triggerFileUpload() {
    const area = document.getElementById('uploadArea');
    const textSpan = document.getElementById('uploadText');

    if (appState.inputType === 'live') {
        // Toggle Recording Simulation
        appState.isRecording = !appState.isRecording;
        if (appState.isRecording) {
            area.classList.add('recording');
            textSpan.innerText = "Recording in progress... (Click to Stop)";
        } else {
            area.classList.remove('recording');
            textSpan.innerText = "Recording stopped. Ready to Execute.";
        }
    } else if (appState.inputType === 'file' || appState.inputType === 'voice') {
        // ADDED: Support for voice file triggering
        document.getElementById('fileInput').click();
    }
    // If text, do nothing (textarea is active)
}

function handleFileSelect(input) {
    if (input.files && input.files[0]) {
        const file = input.files[0];
        appState.selectedFile = file;

        const area = document.getElementById('uploadArea');
        const textSpan = document.getElementById('uploadText');

        // FIXED: Always clear old preview first to prevent duplicates/bugs
        const old = area.querySelector('.preview');
        if (old) old.remove();

        // Image Preview Logic
        if (file.type.startsWith('image/')) {
            const reader = new FileReader();
            reader.onload = function (e) {
                const img = document.createElement('img');
                img.src = e.target.result;
                img.classList.add('preview');
                area.insertBefore(img, textSpan);
                textSpan.innerText = file.name;
            }
            reader.readAsDataURL(file);
        } else {
            textSpan.innerText = `Selected: ${file.name}`;
        }
    }
}

/* --- API INTEGRATION & PROCESSING --- */
async function startProcessing() {
    const btn = document.getElementById('processBtn');
    const overlay = document.getElementById('processingOverlay');
    const statusText = document.getElementById('processStatus');
    const subText = document.querySelector('.process-sub');
    const progressBar = document.getElementById('progressBar');
    const mainContainer = document.getElementById('mainContainer');

    overlay.classList.add('visible');
    mainContainer.style.opacity = '0';
    btn.disabled = true;
    progressBar.style.width = '5%';

    try {
        console.log('Starting real API call...');  // Debug log

        let formData = new FormData();
        formData.append('inputType', appState.inputType);

        if (appState.inputType === 'text') {
            const textarea = document.querySelector('#uploadArea textarea');
            if (textarea && textarea.value.trim()) {
                formData.append('text', textarea.value.trim());
            } else {
                throw new Error("No text provided.");
            }
        } // Add similar for voice/live if implemented

        statusText.innerText = "Extracting Keynotes...";
        subText.innerText = "Processing (1/3)";
        await new Promise(resolve => setTimeout(resolve, 500));
        progressBar.style.width = '33%';

        statusText.innerText = "Generating Detailed Text...";
        subText.innerText = "Processing (2/3)";
        await new Promise(resolve => setTimeout(resolve, 500));
        progressBar.style.width = '66%';

        statusText.innerText = "Constructing Memory Maps...";
        subText.innerText = "Processing (3/3)";

        console.log('Fetching from:', APP_CONFIG.apiEndpoint);  // Debug log
        const response = await fetch(APP_CONFIG.apiEndpoint, {
            method: 'POST',
            body: formData
        });

        if (!response.ok) {
            throw new Error(`API failed with status ${response.status}: ${response.statusText}`);
        }

        const data = await response.json();
        console.log('API Response:', data);  // Debug log - check if custom data arrives
        progressBar.style.width = '100%';

        appState.analysisResult = data.analysis;
        appState.graphData = data.graph || { nodes: [], edges: [] };  // Fallback if graph missing

        renderResults();
        initGraph();  // Ensure graph redraws

        setTimeout(() => {
            overlay.classList.remove('visible');
            btn.disabled = false;
            navigateTo('result-view');
            setTimeout(() => { mainContainer.style.opacity = '1'; }, 50);
        }, 800);

    } catch (error) {
        console.error("API Error Details:", error);
        alert("Connection failed: " + error.message + ". Check console (F12) for details. Is backend running?");
        overlay.classList.remove('visible');
        mainContainer.style.opacity = '1';
        btn.disabled = false;
    }
}

// Helper to simulate individual API delays
function mockApiCall(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// MOCK BACKEND (Returns the final data structure)
function simulateBackendCall() {
    return new Promise(resolve => {
        setTimeout(() => {
            resolve({
                analysis: {
                    summary: "Discussion focused on ethical implications of AI in education. Participants aligned on utility but diverged sharply on privacy protocols.",
                    keyNodes: [
                        "AI personalizes learning vectors.",
                        "Data sovereignty remains critical risk.",
                        "Educator role pivots to facilitation.",
                        "Algorithmic bias requires manual auditing."
                    ]
                },
                graph: {
                    nodes: [
                        { id: 1, type: 'concept', label: "AI in Ed" },
                        { id: 2, type: 'argument', label: "Efficiency" },
                        { id: 3, type: 'argument', label: "Personalization" },
                        { id: 4, type: 'counter', label: "Privacy" },
                        { id: 5, type: 'counter', label: "Bias" },
                        { id: 6, type: 'unresolved', label: "Cost?" },
                    ],
                    edges: [
                        { source: 1, target: 2 }, { source: 1, target: 3 },
                        { source: 1, target: 4 }, { source: 1, target: 5 },
                        { source: 2, target: 5, dashed: true }
                    ]
                }
            });
        }, 2000); // 2 seconds for the final call
    });
}

function renderResults() {
    const summaryEl = document.getElementById('resultSummary');
    const nodesEl = document.getElementById('resultKeyNodes');

    if (appState.analysisResult) {
        summaryEl.innerText = appState.analysisResult.summary;
        nodesEl.innerHTML = '';
        appState.analysisResult.keyNodes.forEach(nodeText => {
            const div = document.createElement('div');
            // UPDATED: Use the new cool class
            div.classList.add('cool-point');
            div.innerHTML = `<i class="fas fa-angle-right" style="margin-right:8px; opacity:0.6;"></i> ${nodeText}`;
            nodesEl.appendChild(div);
        });
    }
}

/* --- GRAPH LOGIC --- */
let canvas, ctx, animationId;

function initGraph() {
    canvas = document.getElementById('knowledgeGraph');
    if (!canvas) return;
    const container = canvas.parentElement;
    canvas.width = container.offsetWidth;
    canvas.height = container.offsetHeight;
    ctx = canvas.getContext('2d');

    if (appState.graphData.nodes.length > 0) {
        const cx = canvas.width / 2;
        const cy = canvas.height / 2;

        const layoutMap = {
            1: { x: 0, y: 0 },
            2: { x: -100, y: -80 },
            3: { x: 100, y: -80 },
            4: { x: -80, y: 100 },
            5: { x: 80, y: 100 },
            6: { x: 150, y: 0 }
        };

        appState.graphData.nodes.forEach(n => {
            const offset = layoutMap[n.id] || { x: (Math.random() - 0.5) * 200, y: (Math.random() - 0.5) * 200 };
            n.x = cx + offset.x;
            n.y = cy + offset.y;
            n.r = n.type === 'concept' ? 25 : 20;
            if (n.type === 'unresolved') n.r = 15;
        });
    }

    if (animationId) cancelAnimationFrame(animationId);
    animateGraph();

    // FIX: Remove existing listener to prevent stacking on multiple navigations
    if (canvas.resizeHandler) window.removeEventListener('resize', canvas.resizeHandler);

    canvas.resizeHandler = () => {
        canvas.width = container.offsetWidth;
        canvas.height = container.offsetHeight;
        drawGraph();
    };

    window.addEventListener('resize', canvas.resizeHandler);
}

function getCSSVar(name) { return getComputedStyle(document.body).getPropertyValue(name).trim(); }

function drawGraph() {
    if (!ctx) return;
    ctx.clearRect(0, 0, canvas.width, canvas.height);
    const lineColor = isDark ? '#4B0082' : '#ccc';
    ctx.lineWidth = 2;

    const nodes = appState.graphData.nodes;
    const edges = appState.graphData.edges;

    edges.forEach(edge => {
        const start = nodes.find(n => n.id === edge.source);
        const end = nodes.find(n => n.id === edge.target);

        if (start && end) {
            ctx.beginPath();
            ctx.moveTo(start.x, start.y);
            ctx.lineTo(end.x, end.y);
            ctx.strokeStyle = lineColor;
            if (edge.dashed) ctx.setLineDash([5, 5]);
            else ctx.setLineDash([]);
            ctx.stroke();
        }
    });
    ctx.setLineDash([]);

    nodes.forEach(node => {
        ctx.beginPath();
        ctx.arc(node.x, node.y, node.r, 0, Math.PI * 2);

        let colorKey = '--node-concept';
        if (node.type === 'argument') colorKey = '--node-argument';
        else if (node.type === 'counter') colorKey = '--node-counter';
        else if (node.type === 'unresolved') colorKey = '--node-unresolved';

        ctx.fillStyle = getCSSVar(colorKey);
        ctx.fill();
        ctx.strokeStyle = '#fff';
        ctx.lineWidth = 3;
        ctx.stroke();

        ctx.fillStyle = isDark ? '#fff' : '#0A192F';
        ctx.font = 'bold 12px Arial';
        ctx.textAlign = 'center';
        ctx.fillText(node.label, node.x, node.y + node.r + 15);
    });
}

function animateGraph() {
    drawGraph();
    animationId = requestAnimationFrame(animateGraph);
}

/* --- REMOVED SMART SCROLL LOGIC --- */
// The scroll event listener for the header has been removed since the header is gone.
