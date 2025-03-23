// Initialize Mermaid
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
    fontSize: 14
});

// Store the graph data globally for use in interpretation
let currentGraphData = null;

// Tab switching
function switchTab(tabId) {
    // Hide all tab contents
    document.querySelectorAll('.tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Deactivate all tabs
    document.querySelectorAll('.tabs .tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected tab content
    document.getElementById(tabId).classList.add('active');
    
    // Activate the clicked tab
    event.currentTarget.classList.add('active');
}

function switchResultTab(tabId) {
    // Hide all result tab contents
    document.querySelectorAll('#code-analysis-results .tab-content').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Deactivate all result tabs
    document.querySelectorAll('#code-analysis-results .tabs .tab').forEach(tab => {
        tab.classList.remove('active');
    });
    
    // Show selected result tab content
    document.getElementById(tabId).classList.add('active');
    
    // Activate the clicked tab
    event.currentTarget.classList.add('active');
}

async function generateDiagram() {
    const inputText = document.getElementById('input-text').value;
    const diagramDiv = document.getElementById('text-diagram');
    
    if (!inputText.trim()) {
        diagramDiv.innerHTML = '<div class="error">Please enter some text to generate a diagram.</div>';
        return;
    }
    
    diagramDiv.innerHTML = '<div class="loading">Generating diagram...</div>';
    
    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: inputText })
        });
        
        const data = await response.json();
        
        if (data.error) {
            diagramDiv.innerHTML = `<div class="error">${data.error}</div>`;
            return;
        }
        
        // Clear previous content
        diagramDiv.innerHTML = '';
        
        // Create a new div for mermaid
        const mermaidDiv = document.createElement('div');
        mermaidDiv.className = 'mermaid';
        mermaidDiv.textContent = data.graph_code;
        diagramDiv.appendChild(mermaidDiv);
        
        // Reinitialize mermaid
        await mermaid.run();
        
        // Setup diagram controls
        setupDiagramControls('text-diagram');
    } catch (error) {
        diagramDiv.innerHTML = `<div class="error">Error generating diagram: ${error.message}</div>`;
    }
}

async function analyzeCode() {
    const directoryPath = document.getElementById('directory-path').value;
    
    if (!directoryPath.trim()) {
        alert('Please enter a directory path');
        return;
    }
    
    // Show loading state
    document.getElementById('loading').style.display = 'block';
    document.getElementById('code-analysis-results').style.display = 'none';
    
    try {
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ directory: directoryPath })
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert(`Error: ${data.error}`);
            document.getElementById('loading').style.display = 'none';
            return;
        }
        
        // Store the graph data globally
        currentGraphData = data;
        
        // Generate mermaid diagram from the graph data
        generateCodeStructureDiagram(data);
        
        // Populate node list
        populateNodeList(data.nodes);
        
        // Hide loading, show results
        document.getElementById('loading').style.display = 'none';
        document.getElementById('code-analysis-results').style.display = 'block';
    } catch (error) {
        alert(`Error analyzing code: ${error.message}`);
        document.getElementById('loading').style.display = 'none';
    }
}

async function analyzeGitHubRepo() {
    const repoUrl = document.getElementById('repo-url').value;
    const branch = document.getElementById('repo-branch').value || 'main';
    
    // Get filter options (you'll need to add these UI elements)
    const nodeTypes = Array.from(document.querySelectorAll('#node-type-filter:checked'))
        .map(checkbox => checkbox.value);
    const edgeTypes = Array.from(document.querySelectorAll('#edge-type-filter:checked'))
        .map(checkbox => checkbox.value);
    const searchTerm = document.getElementById('search-term')?.value || '';
    const maxNodes = parseInt(document.getElementById('max-nodes')?.value || '0');
    
    if (!repoUrl) {
        alert('Please enter a GitHub repository URL');
        return;
    }
    
    // Show loading state
    document.getElementById('loading').style.display = 'block';
    document.getElementById('code-analysis-results').style.display = 'none';
    
    try {
        const response = await fetch('/analyze_github', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                repo_url: repoUrl,
                branch: branch,
                node_types: nodeTypes,
                edge_types: edgeTypes,
                search_term: searchTerm,
                max_nodes: maxNodes
            })
        });
        
        const data = await response.json();
        
        if (data.error) {
            alert(`Error: ${data.error}`);
            document.getElementById('loading').style.display = 'none';
            return;
        }
        
        // Process results as before
        currentGraphData = data;
        generateCodeStructureDiagram(data);
        populateNodeList(data.nodes);
        
        document.getElementById('loading').style.display = 'none';
        document.getElementById('code-analysis-results').style.display = 'block';
    } catch (error) {
        alert(`Error analyzing repository: ${error.message}`);
        document.getElementById('loading').style.display = 'none';
    }
}

function generateCodeStructureDiagram(graphData) {
    const diagramDiv = document.getElementById('code-diagram');
    
    // Create mermaid code from graph data
    let mermaidCode = 'graph TD\n';
    
    // Add nodes
    graphData.nodes.forEach(node => {
        const nodeId = node.id.replace(/[^a-zA-Z0-9]/g, '_'); // Make ID mermaid-compatible
        const nodeDisplay = node.display_id;
        const nodeType = node.type;
        
        let nodeStyle = '';
        if (nodeType === 'file') {
            nodeStyle = 'fill:#e3f2fd,stroke:#2196F3';
        } else if (nodeType === 'function') {
            nodeStyle = 'fill:#e8f5e9,stroke:#4CAF50';
        } else if (nodeType === 'event_handler') {
            nodeStyle = 'fill:#fff3e0,stroke:#FF9800';
        }
        
        mermaidCode += `    ${nodeId}["${nodeDisplay}"]${nodeStyle ? ':::' + nodeType : ''}\n`;
    });
    
    // Add class styles
    mermaidCode += '    classDef file fill:#e3f2fd,stroke:#2196F3\n';
    mermaidCode += '    classDef function fill:#e8f5e9,stroke:#4CAF50\n';
    mermaidCode += '    classDef event_handler fill:#fff3e0,stroke:#FF9800\n';
    
    // Add edges with different styling based on type
    graphData.edges.forEach(edge => {
        const sourceId = edge.source.replace(/[^a-zA-Z0-9]/g, '_');
        const targetId = edge.target.replace(/[^a-zA-Z0-9]/g, '_');
        const edgeType = edge.type;
        
        let arrowStyle = '-->';
        if (edgeType === 'contains') {
            arrowStyle = '-.->'; // Dotted arrow
        } else if (edgeType === 'imports') {
            arrowStyle = '==>'; // Thick arrow
        }
        
        mermaidCode += `    ${sourceId} ${arrowStyle}|${edgeType}| ${targetId}\n`;
    });
    
    // Create a new div for mermaid
    diagramDiv.innerHTML = '';
    const mermaidDiv = document.createElement('div');
    mermaidDiv.className = 'mermaid';
    mermaidDiv.textContent = mermaidCode;
    diagramDiv.appendChild(mermaidDiv);
    
    // Reinitialize mermaid
    mermaid.run();
    
    // Setup diagram controls
    setTimeout(() => setupDiagramControls('code-diagram'), 500);
}

function populateNodeList(nodes) {
    const nodeListDiv = document.getElementById('node-list');
    nodeListDiv.innerHTML = '';
    
    // Sort nodes by type and name
    const sortedNodes = [...nodes].sort((a, b) => {
        if (a.type !== b.type) {
            return a.type.localeCompare(b.type);
        }
        return a.name.localeCompare(b.name);
    });
    
    sortedNodes.forEach(node => {
        const nodeDiv = document.createElement('div');
        nodeDiv.className = `node-item node-${node.type}`;
        nodeDiv.innerHTML = `<strong>${node.name}</strong> (${node.type})`;
        nodeListDiv.appendChild(nodeDiv);
    });
}

async function interpretCodeStructure() {
    if (!currentGraphData) {
        alert('Please analyze code first');
        return;
    }
    
    const interpretationDiv = document.getElementById('ai-interpretation');
    interpretationDiv.innerHTML = '<p>Generating interpretation...</p>';
    
    // Convert graph data to text description
    let description = 'Code structure analysis:\n\n';
    
    // Add node counts by type
    const nodeTypes = {};
    currentGraphData.nodes.forEach(node => {
        if (!nodeTypes[node.type]) {
            nodeTypes[node.type] = 0;
        }
        nodeTypes[node.type]++;
    });
    
    description += 'Components:\n';
    Object.entries(nodeTypes).forEach(([type, count]) => {
        description += `- ${count} ${type}(s)\n`;
    });
    
    // Add edge information
    const edgeTypes = {};
    currentGraphData.edges.forEach(edge => {
        if (!edgeTypes[edge.type]) {
            edgeTypes[edge.type] = 0;
        }
        edgeTypes[edge.type]++;
    });
    
    description += '\nRelationships:\n';
    Object.entries(edgeTypes).forEach(([type, count]) => {
        description += `- ${count} ${type} relationship(s)\n`;
    });
    
    // Add some specific relationship examples
    description += '\nKey relationships:\n';
    for (let i = 0; i < Math.min(5, currentGraphData.edges.length); i++) {
        const edge = currentGraphData.edges[i];
        const sourceNode = currentGraphData.nodes.find(n => n.id === edge.source);
        const targetNode = currentGraphData.nodes.find(n => n.id === edge.target);
        if (sourceNode && targetNode) {
            description += `- ${sourceNode.name} ${edge.type} ${targetNode.name}\n`;
        }
    }
    
    description += '\nPlease describe this code structure, identify architectural patterns, and suggest improvements.';
    
    try {
        const response = await fetch('/generate', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ text: description })
        });
        
        const data = await response.json();
        
        if (data.error) {
            interpretationDiv.innerHTML = `<div class="error">${data.error}</div>`;
            return;
        }
        
        // Display the interpretation as text (not as a diagram)
        interpretationDiv.innerHTML = `<div class="interpretation-text">${data.graph_code.replace(/graph TD/i, '<b>Analysis:</b>').replace(/\n/g, '<br>').replace(/^\s{4}/gm, '')}</div>`;
        
    } catch (error) {
        interpretationDiv.innerHTML = `<div class="error">Error generating interpretation: ${error.message}</div>`;
    }
}

// Add zoom/pan functionality to diagrams
function setupDiagramControls(containerId) {
    const container = document.getElementById(containerId);
    if (!container) return;
    
    // Add controls
    const controlsDiv = document.createElement('div');
    controlsDiv.className = 'diagram-controls';
    controlsDiv.innerHTML = `
        <button onclick="zoomDiagram('${containerId}', 1.2)">+</button>
        <button onclick="zoomDiagram('${containerId}', 0.8)">-</button>
        <button onclick="resetDiagram('${containerId}')">Reset</button>
        <button onclick="toggleFullscreen('${containerId}')">Full</button>
    `;
    container.appendChild(controlsDiv);
    
    // Set initial scale
    const diagram = container.querySelector('.mermaid');
    if (diagram) {
        diagram.style.transform = 'scale(1)';
        diagram.style.transformOrigin = 'top left';
    }
}

function zoomDiagram(containerId, factor) {
    const container = document.getElementById(containerId);
    const diagram = container.querySelector('.mermaid');
    if (!diagram) return;
    
    const currentScale = parseFloat(diagram.style.transform.replace('scale(', '').replace(')', '') || '1');
    const newScale = currentScale * factor;
    diagram.style.transform = `scale(${newScale})`;
}

function resetDiagram(containerId) {
    const container = document.getElementById(containerId);
    const diagram = container.querySelector('.mermaid');
    if (diagram) {
        diagram.style.transform = 'scale(1)';
    }
}

function toggleFullscreen(containerId) {
    const container = document.getElementById(containerId);
    if (!document.fullscreenElement) {
        container.requestFullscreen().catch(err => {
            alert(`Error attempting to enable fullscreen: ${err.message}`);
        });
    } else {
        document.exitFullscreen();
    }
}

// Make sure to implement the uploadCodebase function if it's used in the HTML
function uploadCodebase() {
    alert("Upload functionality not implemented yet");
}