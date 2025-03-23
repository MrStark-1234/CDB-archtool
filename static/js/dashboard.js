// Initialize Mermaid with more robust error handling
mermaid.initialize({
    startOnLoad: true,
    theme: 'default',
    securityLevel: 'loose',
    flowchart: {
        useMaxWidth: false,
        htmlLabels: true,
        curve: 'basis'
    },
    maxTextSize: 50000,
    fontSize: 14,
    logLevel: 'error' // Only show errors, not warnings
});

// Helper function to ensure consistent node ID sanitization
function sanitizeNodeId(id) {
    // Replace all non-alphanumeric characters with underscores
    return String(id).replace(/[^a-zA-Z0-9]/g, '_');
}

// New helper function to validate and fix Mermaid syntax
function validateMermaidSyntax(code) {
    // Basic validation and fixes for common issues
    if (!code) return "graph TD\n    A[No data available]";
    
    // Ensure graph definition starts correctly
    if (!code.trim().startsWith('graph')) {
        code = 'graph TD\n' + code;
    }
    
    // Fix common syntax issues
    code = code
        .replace(/"/g, '\\"') // Escape double quotes inside node text
        .replace(/\n\s*\n/g, '\n') // Remove empty lines
        .replace(/&/g, 'and') // Replace ampersands
        .replace(/</g, '&lt;') // Replace < with HTML entity
        .replace(/>/g, '&gt;'); // Replace > with HTML entity
    
    return code;
}

// Handle folder upload and trigger analysis
function handleFolderUpload(event) {
    const files = event.target.files;
    if (files.length > 0) {
        // Simulate analyzing the uploaded folder
        analyzeCode(files);
    }
}

// Update the analyzeCode function with better error handling
async function analyzeCode(files) {
    document.getElementById('loading').style.display = 'block';
    document.getElementById('code-analysis-results').style.display = 'none';

    try {
        const folderData = Array.from(files).map(file => file.webkitRelativePath);
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ folder: folderData })
        });
        const data = await response.json();

        if (data.error) {
            alert(`Error: ${data.error}`);
            document.getElementById('loading').style.display = 'none';
            return;
        }

        // Validate and fix graph code before rendering
        let graphCode = validateMermaidSyntax(data.graph_code);
        
        // For debugging - log the sanitized code
        console.log("Rendering Mermaid diagram with code:", graphCode);
        
        // Display the analyzed diagram with error handling
        const diagramContainer = document.getElementById('code-diagram');
        diagramContainer.innerHTML = `<div class="mermaid">${graphCode}</div>`;
        
        try {
            await mermaid.run();
        } catch (mermaidError) {
            console.error("Mermaid rendering error:", mermaidError);
            diagramContainer.innerHTML = `
                <div class="error-message" style="color: #ff48c4; padding: 20px;">
                    <h3>Error Rendering Diagram</h3>
                    <p>${mermaidError.message || "Syntax error in diagram"}</p>
                    <p>Please try with a different codebase or report this issue.</p>
                    <div class="code-preview">
                        <h4>Diagram
                    </div>
                </div>`;
        }

        document.getElementById('loading').style.display = 'none';
        document.getElementById('code-analysis-results').style.display = 'block';
    } catch (error) {
        alert(`Error analyzing code: ${error.message}`);
        document.getElementById('loading').style.display = 'none';
    }
}