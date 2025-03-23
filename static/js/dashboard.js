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

// Handle folder upload and trigger analysis
function handleFolderUpload(event) {
    const files = event.target.files;
    if (files.length > 0) {
        // Simulate analyzing the uploaded folder
        analyzeCode(files);
    }
}

async function analyzeCode(files) {
    document.getElementById('loading').style.display = 'block';
    document.getElementById('code-analysis-results').style.display = 'none';

    try {
        // Simulate an API call to analyze the folder
        const folderData = Array.from(files).map(file => file.webkitRelativePath);
        const response = await fetch('/analyze', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ folder: folderData }) // Send folder structure
        });
        const data = await response.json();

        if (data.error) {
            alert(`Error: ${data.error}`);
            document.getElementById('loading').style.display = 'none';
            return;
        }

        // Display the analyzed diagram
        document.getElementById('code-diagram').innerHTML = `<div class="mermaid">${data.graph_code}</div>`;
        await mermaid.run();

        document.getElementById('loading').style.display = 'none';
        document.getElementById('code-analysis-results').style.display = 'block';
    } catch (error) {
        alert(`Error analyzing code: ${error.message}`);
        document.getElementById('loading').style.display = 'none';
    }
}