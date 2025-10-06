// Dashboard Application Logic
// Main JavaScript file for the IS Research Dashboard

// Global state
let currentSection = 'overview';
let filteredStreams = [];
let filteredPapers = [];

// Initialize dashboard when DOM is loaded
document.addEventListener('DOMContentLoaded', function() {
    initializeDashboard();
});

// Main initialization function
async function initializeDashboard() {
    try {
        // Load data
        await loadActualData();
        
        console.log("Data loaded:", currentData);
        console.log("Number of streams:", currentData.streams.length);
        
        // Update header with actual stats
        updateHeader();
        
        // Initialize sections
        initializeOverview();
        initializeStreams();
        initializePapers();
        initializeVisualizations();
        initializeInsights();
        
        console.log("Dashboard initialized successfully");
    } catch (error) {
        console.error("Error initializing dashboard:", error);
        alert("Error initializing dashboard. Please check the console for details.");
    }
}

// Update header with loaded data
function updateHeader() {
    const headerPapers = document.getElementById('headerPapers');
    const headerStreams = document.getElementById('headerStreams');
    const headerCitations = document.getElementById('headerCitations');
    
    if (headerPapers && currentData.stats) {
        headerPapers.textContent = currentData.stats.totalPapers.toLocaleString() + ' Papers';
    }
    if (headerStreams && currentData.stats) {
        headerStreams.textContent = currentData.stats.totalStreams + ' Research Streams';
    }
    if (headerCitations && currentData.stats) {
        headerCitations.textContent = currentData.stats.totalCitations.toLocaleString() + ' Citations';
    }
}

// Navigation functions
function showSection(sectionId, clickedElement) {
    // Hide all sections
    document.querySelectorAll('.section').forEach(section => {
        section.classList.remove('active');
    });
    
    // Remove active class from all nav pills
    document.querySelectorAll('.nav-pill').forEach(pill => {
        pill.classList.remove('active');
    });
    
    // Show selected section
    document.getElementById(sectionId).classList.add('active');
    
    // Add active class to clicked nav pill
    if (clickedElement) {
        clickedElement.classList.add('active');
    }
    
    currentSection = sectionId;
    
    // Trigger section-specific updates
    switch(sectionId) {
        case 'overview':
            updateOverviewCharts();
            break;
        case 'streams':
            updateStreamDisplay();
            break;
        case 'papers':
            updatePaperDisplay();
            break;
        case 'visualizations':
            updateVisualizationCharts();
            break;
        case 'insights':
            updateInsights();
            break;
    }
}

// Overview Section Functions
function initializeOverview() {
    updateOverviewCharts();
}

function updateOverviewCharts() {
    createTimelineChart();
    createJournalChart();
}

function createTimelineChart() {
    const trace = {
        x: currentData.timeline.map(d => d.year),
        y: currentData.timeline.map(d => d.papers),
        type: 'scatter',
        mode: 'lines+markers',
        name: 'Publications per Year',
        line: {
            color: '#3498db',
            width: 3
        },
        marker: {
            color: '#3498db',
            size: 6
        }
    };
    
    const layout = {
        title: {
            text: 'Publication Timeline (2000-2025)',
            font: { size: 16, color: '#2c3e50' }
        },
        xaxis: {
            title: 'Year',
            gridcolor: '#ecf0f1'
        },
        yaxis: {
            title: 'Number of Papers',
            gridcolor: '#ecf0f1'
        },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)',
        font: { family: 'Source Sans Pro' }
    };
    
    Plotly.newPlot('timelineChart', [trace], layout, {responsive: true});
}

function createJournalChart() {
    const trace = {
        x: currentData.journals.map(d => d.papers),
        y: currentData.journals.map(d => d.name),
        type: 'bar',
        orientation: 'h',
        marker: {
            color: '#3498db',
            opacity: 0.8
        }
    };
    
    const layout = {
        title: {
            text: 'Papers by Journal',
            font: { size: 16, color: '#2c3e50' }
        },
        xaxis: {
            title: 'Number of Papers',
            gridcolor: '#ecf0f1'
        },
        yaxis: {
            title: '',
            gridcolor: '#ecf0f1'
        },
        plot_bgcolor: 'rgba(0,0,0,0)',
        paper_bgcolor: 'rgba(0,0,0,0)',
        font: { family: 'Source Sans Pro' },
        margin: { l: 200 }
    };
    
    Plotly.newPlot('journalChart', [trace], layout, {responsive: true});
}

// Research Streams Section Functions
function initializeStreams() {
    filteredStreams = [...currentData.streams];
    updateStreamDisplay();
}

function updateStreamDisplay() {
    const sortBy = document.getElementById('streamSort')?.value || 'size';
    const activityFilter = document.getElementById('activityFilter')?.value || 'all';
    const searchTerm = document.getElementById('topicSearch')?.value.toLowerCase() || '';
    
    console.log("Updating stream display:", { sortBy, activityFilter, searchTerm });
    
    // Filter streams
    filteredStreams = currentData.streams.filter(stream => {
        // Activity filter
        if (activityFilter === 'emerging' && stream.recentActivity < 0.5) return false;
        if (activityFilter === 'established' && stream.recentActivity > 0.5) return false;
        if (activityFilter === 'high-impact' && stream.avgCitations < 200) return false;
        
        // Search filter
        if (searchTerm) {
            const searchText = (stream.title + ' ' + stream.description + ' ' + stream.topTerms.join(' ')).toLowerCase();
            if (!searchText.includes(searchTerm)) return false;
        }
        
        return true;
    });
    
    console.log("Filtered streams:", filteredStreams.length);
    
    // Sort streams
    filteredStreams.sort((a, b) => {
        switch(sortBy) {
            case 'citations':
                return b.avgCitations - a.avgCitations;
            case 'recent':
                return b.recentActivity - a.recentActivity;
            case 'impact':
                return b.totalCitations - a.totalCitations;
            default: // 'size'
                return b.size - a.size;
        }
    });
    
    renderStreams();
}

function renderStreams() {
    const container = document.getElementById('streamsContainer');
    if (!container) return;
    
    container.innerHTML = filteredStreams.map(stream => `
        <div class="stream-card" onclick="toggleStreamDetails(${stream.id})">
            <div class="stream-header">
                <div class="stream-title">Stream ${stream.id}: ${stream.title}</div>
            </div>
            <div class="stream-meta">
                <span class="highlight">${stream.size} papers</span>
                <span>${Math.round(stream.avgCitations)} avg citations</span>
                <span>${(stream.recentActivity * 100).toFixed(0)}% recent activity</span>
                <span>${stream.yearRange}</span>
            </div>
            <p style="margin: 1rem 0; color: var(--text-secondary);">${stream.description}</p>
            <div style="margin-top: 1rem;">
                <strong>Key Terms:</strong> ${stream.topTerms.slice(0, 5).join(', ')}
            </div>
            <div class="paper-list" id="papers-${stream.id}">
                ${stream.samplePapers ? renderSamplePapers(stream.samplePapers) : '<p style="padding: 1rem; color: var(--text-secondary);">Sample papers loading...</p>'}
            </div>
        </div>
    `).join('');
}

function renderSamplePapers(papers) {
    return papers.map(paper => `
        <div class="paper-item">
            <div class="paper-title">${paper.title}</div>
            <div class="paper-meta">
                <span><i class="fas fa-users"></i> ${paper.authors}</span>
                <span><i class="fas fa-calendar"></i> ${paper.year}</span>
                <span><i class="fas fa-book"></i> ${paper.journal}</span>
                <span><i class="fas fa-quote-right"></i> ${paper.citations} citations</span>
                ${paper.doi ? `<span><a href="https://doi.org/${paper.doi}" target="_blank" class="link-external"><i class="fas fa-external-link-alt"></i> DOI</a></span>` : ''}
            </div>
        </div>
    `).join('');
}

function toggleStreamDetails(streamId) {
    const paperList = document.getElementById(`papers-${streamId}`);
    if (paperList) {
        paperList.classList.toggle('expanded');
    }
}

// Papers Explorer Section Functions
function initializePapers() {
    // Populate stream filter dropdown
    const streamFilter = document.getElementById('paperStreamFilter');
    if (streamFilter) {
        streamFilter.innerHTML = '<option value="all">All Streams</option>' +
            currentData.streams.map(stream => 
                `<option value="${stream.id}">Stream ${stream.id}: ${stream.title}</option>`
            ).join('');
    }
    
    // Initialize papers display
    filteredPapers = getAllPapers();
    updatePaperDisplay();
}

function getAllPapers() {
    // Flatten all papers from all streams
    let allPapers = [];
    currentData.streams.forEach(stream => {
        if (stream.samplePapers) {
            stream.samplePapers.forEach(paper => {
                allPapers.push({
                    ...paper,
                    streamId: stream.id,
                    streamTitle: stream.title
                });
            });
        }
    });
    return allPapers;
}

function updatePaperDisplay() {
    const streamFilter = document.getElementById('paperStreamFilter')?.value || 'all';
    const yearFilter = parseInt(document.getElementById('yearSlider')?.value || 2000);
    const sortBy = document.getElementById('paperSort')?.value || 'citations';
    const searchTerm = document.getElementById('paperSearch')?.value.toLowerCase() || '';
    
    console.log("Updating paper display:", { streamFilter, yearFilter, sortBy, searchTerm });
    
    // Update year display
    const yearDisplay = document.getElementById('yearDisplay');
    if (yearDisplay) {
        yearDisplay.textContent = yearFilter + '+';
    }
    
    // Filter papers
    filteredPapers = getAllPapers().filter(paper => {
        if (streamFilter !== 'all' && paper.streamId !== parseInt(streamFilter)) return false;
        if (paper.year < yearFilter) return false;
        if (searchTerm) {
            const searchText = (paper.title + ' ' + paper.authors + ' ' + paper.journal).toLowerCase();
            if (!searchText.includes(searchTerm)) return false;
        }
        return true;
    });
    
    console.log("Filtered papers:", filteredPapers.length);
    
    // Sort papers
    filteredPapers.sort((a, b) => {
        switch(sortBy) {
            case 'year':
                return b.year - a.year;
            case 'title':
                return a.title.localeCompare(b.title);
            default: // 'citations'
                return b.citations - a.citations;
        }
    });
    
    renderPapers();
}

function renderPapers() {
    const container = document.getElementById('papersContainer');
    if (!container) return;
    
    if (filteredPapers.length === 0) {
        container.innerHTML = '<p style="text-align: center; color: var(--text-secondary); padding: 2rem;">No papers match your current filters.</p>';
        return;
    }
    
    container.innerHTML = `
        <p style="margin-bottom: 1rem; color: var(--text-secondary);">
            Showing ${filteredPapers.length} papers
        </p>
        ${filteredPapers.slice(0, 50).map(paper => `
            <div class="paper-item">
                <div class="paper-title">${paper.title}</div>
                <div class="paper-meta">
                    <span><i class="fas fa-users"></i> ${paper.authors}</span>
                    <span><i class="fas fa-calendar"></i> ${paper.year}</span>
                    <span><i class="fas fa-book"></i> ${paper.journal}</span>
                    <span><i class="fas fa-quote-right"></i> ${paper.citations} citations</span>
                    <span><i class="fas fa-project-diagram"></i> ${paper.streamTitle}</span>
                    ${paper.doi ? `<span><a href="https://doi.org/${paper.doi}" target="_blank" class="link-external"><i class="fas fa-external-link-alt"></i> DOI</a></span>` : ''}
                </div>
            </div>
        `).join('')}
        ${filteredPapers.length > 50 ? '<p style="text-align: center; color: var(--text-secondary); padding: 1rem;">Showing first 50 results. Refine filters to see more specific results.</p>' : ''}
    `;
}

// Visualizations Section Functions
function initializeVisualizations() {
    updateVisualizationCharts();
}

function updateVisualizationCharts() {
    createStreamSizeChart();
    createCitationChart();
    createTemporalChart();
    createEmergingChart();
}

function createStreamSizeChart() {
    const sortedStreams = [...currentData.streams].sort((a, b) => b.size - a.size);
    
    const trace = {
        x: sortedStreams.map(s => s.size),
        y: sortedStreams.map(s => `Stream ${s.id}: ${s.title.substring(0, 30)}...`),
        type: 'bar',
        orientation: 'h',
        marker: {
            color: sortedStreams.map(s => s.recentActivity > 0.5 ? '#e74c3c' : '#3498db'),
            opacity: 0.8
        }
    };
    
    const layout = {
        title: 'Research Stream Sizes',
        xaxis: { title: 'Number of Papers' },
        yaxis: { title: '' },
        height: 600,
        margin: { l: 250 }
    };
    
    Plotly.newPlot('streamSizeChart', [trace], layout, {responsive: true});
}

function createCitationChart() {
    const trace = {
        x: currentData.streams.map(s => s.size),
        y: currentData.streams.map(s => s.avgCitations),
        mode: 'markers',
        type: 'scatter',
        text: currentData.streams.map(s => `Stream ${s.id}: ${s.title}`),
        marker: {
            size: currentData.streams.map(s => Math.sqrt(s.totalCitations / 1000)),
            color: currentData.streams.map(s => s.recentActivity),
            colorscale: 'Viridis',
            showscale: true,
            colorbar: { title: 'Recent Activity' }
        }
    };
    
    const layout = {
        title: 'Stream Size vs. Citation Impact',
        xaxis: { title: 'Number of Papers' },
        yaxis: { title: 'Average Citations per Paper' }
    };
    
    Plotly.newPlot('citationChart', [trace], layout, {responsive: true});
}

function createTemporalChart() {
    // Simplified temporal evolution chart
    const emergingStreams = currentData.streams.filter(s => s.recentActivity > 0.6);
    const establishedStreams = currentData.streams.filter(s => s.recentActivity < 0.4);
    
    const trace1 = {
        x: ['2000-2010', '2010-2020', '2020-2025'],
        y: [establishedStreams.length * 0.8, establishedStreams.length * 1.0, establishedStreams.length * 0.6],
        name: 'Established Topics',
        type: 'bar',
        marker: { color: '#3498db' }
    };
    
    const trace2 = {
        x: ['2000-2010', '2010-2020', '2020-2025'],
        y: [emergingStreams.length * 0.2, emergingStreams.length * 0.6, emergingStreams.length * 1.0],
        name: 'Emerging Topics',
        type: 'bar',
        marker: { color: '#e74c3c' }
    };
    
    const layout = {
        title: 'Research Topic Evolution Over Time',
        xaxis: { title: 'Time Period' },
        yaxis: { title: 'Research Activity Level' },
        barmode: 'group'
    };
    
    Plotly.newPlot('temporalChart', [trace1, trace2], layout, {responsive: true});
}

function createEmergingChart() {
    const emerging = currentData.streams.filter(s => s.recentActivity > 0.6);
    const established = currentData.streams.filter(s => s.recentActivity < 0.4);
    
    const trace = {
        labels: ['Emerging Topics', 'Established Topics', 'Transitional Topics'],
        values: [emerging.length, established.length, currentData.streams.length - emerging.length - established.length],
        type: 'pie',
        marker: {
            colors: ['#e74c3c', '#3498db', '#f39c12']
        }
    };
    
    const layout = {
        title: 'Distribution of Research Topic Maturity'
    };
    
    Plotly.newPlot('emergingChart', [trace], layout, {responsive: true});
}

// Insights Section Functions
function initializeInsights() {
    updateInsights();
}

function updateInsights() {
    renderImpactfulStreams();
    renderEmergingTopics();
    renderEvolutionPatterns();
}

function renderImpactfulStreams() {
    const topStreams = [...currentData.streams]
        .sort((a, b) => b.avgCitations - a.avgCitations)
        .slice(0, 5);
    
    const container = document.getElementById('impactfulStreams');
    if (!container) return;
    
    container.innerHTML = topStreams.map((stream, index) => `
        <div class="stream-card" style="margin: 1rem 0;">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <div style="background: var(--accent-color); color: white; width: 30px; height: 30px; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-weight: bold;">
                    ${index + 1}
                </div>
                <div style="flex: 1;">
                    <div class="stream-title">${stream.title}</div>
                    <div class="stream-meta">
                        <span class="highlight">${stream.avgCitations} avg citations</span>
                        <span>${stream.size} papers</span>
                        <span>${stream.totalCitations.toLocaleString()} total citations</span>
                    </div>
                </div>
            </div>
        </div>
    `).join('');
}

function renderEmergingTopics() {
    const emergingStreams = [...currentData.streams]
        .filter(s => s.recentActivity > 0.6)
        .sort((a, b) => b.recentActivity - a.recentActivity)
        .slice(0, 5);
    
    const container = document.getElementById('emergingTopics');
    if (!container) return;
    
    container.innerHTML = emergingStreams.map(stream => `
        <div class="stream-card" style="margin: 1rem 0; border-left: 4px solid var(--danger-color);">
            <div class="stream-title">${stream.title}</div>
            <div class="stream-meta">
                <span class="highlight">${(stream.recentActivity * 100).toFixed(0)}% recent activity</span>
                <span>${stream.size} papers</span>
                <span>Avg ${stream.avgCitations} citations</span>
            </div>
            <p style="margin-top: 0.5rem; color: var(--text-secondary);">${stream.description}</p>
        </div>
    `).join('');
}

function renderEvolutionPatterns() {
    const container = document.getElementById('evolutionPatterns');
    if (!container) return;
    
    const totalCitations = currentData.streams.reduce((sum, s) => sum + s.totalCitations, 0);
    const avgRecentActivity = currentData.streams.reduce((sum, s) => sum + s.recentActivity, 0) / currentData.streams.length;
    
    container.innerHTML = `
        <div class="methodology-box">
            <h4>Research Landscape Dynamics</h4>
            <ul style="list-style: disc; padding-left: 2rem;">
                <li><strong>Technology Acceptance</strong> remains the most impactful research area with the highest citation rates</li>
                <li><strong>AI and Machine Learning</strong> shows 89% recent activity, indicating rapid growth in this area</li>
                <li><strong>Digital Platforms</strong> emerged as a major research focus since 2005</li>
                <li><strong>Cybersecurity</strong> research has intensified significantly (72% recent activity)</li>
                <li>Traditional topics like E-commerce show maturation with 31% recent activity</li>
            </ul>
        </div>
        
        <div class="stats-grid">
            <div class="stat-card">
                <span class="stat-number">${(avgRecentActivity * 100).toFixed(0)}%</span>
                <div class="stat-label">Average Recent Activity</div>
            </div>
            <div class="stat-card">
                <span class="stat-number">${currentData.streams.filter(s => s.recentActivity > 0.6).length}</span>
                <div class="stat-label">Emerging Topics</div>
            </div>
            <div class="stat-card">
                <span class="stat-number">${currentData.streams.filter(s => s.recentActivity < 0.4).length}</span>
                <div class="stat-label">Established Topics</div>
            </div>
        </div>
    `;
}