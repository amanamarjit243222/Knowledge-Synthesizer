export const APP_CONFIG = {
    apiEndpoint: "http://localhost:8000/synthesize",
    mockDelay: 1500
};

export const INITIAL_STATE = {
    inputType: 'live',
    discType: 'roundtable',
    selectedFile: null,
    isRecording: false,
    graphData: { nodes: [], edges: [] },
    analysisResult: null
};
