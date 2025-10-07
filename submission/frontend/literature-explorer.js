// Literature Explorer JavaScript
// Loads and displays hierarchical clustering results

class LiteratureExplorer {
    constructor() {
        this.data = {
            papers: [],
            level1: [],
            level2: [],
            citationStats: {}
        };
        this.currentView = 'topics';
        this.currentStream = 'all';
        this.currentL2 = null;
        this.searchQuery = '';
        this.activeFilter = 'all';
        
        this.init();
    }

    async init() {
        await this.loadData();
        this.setupEventListeners();
        this.renderStreamList();
        this.renderContent();
    }

    async loadData() {
        try {
            // Load all data files from 3-level clustering
            const [papers, level1, level2, level3, citStats] = await Promise.all([
                this.loadCSV('./data/clean/hybrid_streams_3level/doc_assignments.csv'),
                this.loadCSV('./data/clean/hybrid_streams_3level/topics_level1.csv'),
                this.loadCSV('./data/clean/hybrid_streams_3level/topics_level2.csv'),
                this.loadCSV('./data/clean/hybrid_streams_3level/topics_level3.csv'),
                fetch('./data/clean/hybrid_streams_3level/citation_network_stats.json').then(r => r.json())
            ]);

            this.data.papers = papers;
            this.data.level1 = level1;
            this.data.level2 = level2;
            this.data.level3 = level3;
            this.data.citationStats = citStats;

            console.log('Data loaded:', {
                papers: this.data.papers.length,
                level1: this.data.level1.length,
                level2: this.data.level2.length,
                level3: this.data.level3.length
            });
        } catch (error) {
            console.error('Error loading data:', error);
            this.showError('Failed to load data. Please ensure data files are in the correct location.');
        }
    }

    async loadCSV(url) {
        const response = await fetch(url);
        const text = await response.text();
        return this.parseCSV(text);
    }

    parseCSV(text) {
        const lines = text.trim().split('\n');
        const headers = lines[0].split(',').map(h => h.trim().replace(/^"|"$/g, ''));
        
        return lines.slice(1).map(line => {
            // Simple CSV parser - handles quoted fields
            const values = [];
            let current = '';
            let inQuotes = false;
            
            for (let char of line) {
                if (char === '"') {
                    inQuotes = !inQuotes;
                } else if (char === ',' && !inQuotes) {
                    values.push(current.trim().replace(/^"|"$/g, ''));
                    current = '';
                } else {
                    current += char;
                }
            }
            values.push(current.trim().replace(/^"|"$/g, ''));
            
            const obj = {};
            headers.forEach((header, i) => {
                obj[header] = values[i] || '';
            });
            return obj;
        });
    }

    setupEventListeners() {
        // Search
        document.getElementById('search-input').addEventListener('input', (e) => {
            this.searchQuery = e.target.value.toLowerCase();
            this.renderContent();
        });

        // Filter chips
        document.querySelectorAll('.chip').forEach(chip => {
            chip.addEventListener('click', (e) => {
                document.querySelectorAll('.chip').forEach(c => c.classList.remove('active'));
                e.target.classList.add('active');
                this.activeFilter = e.target.dataset.filter;
                this.renderContent();
            });
        });

        // View toggle
        document.querySelectorAll('.view-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                document.querySelectorAll('.view-btn').forEach(b => b.classList.remove('active'));
                e.target.classList.add('active');
                this.currentView = e.target.dataset.view;
                this.renderContent();
            });
        });
    }

    renderStreamList() {
        const streamList = document.getElementById('stream-list');
        const allItem = streamList.querySelector('[data-stream="all"]');
        
        this.data.level1.forEach(stream => {
            const li = document.createElement('li');
            li.className = 'stream-item';
            li.dataset.stream = stream.L1;
            
            li.innerHTML = `
                <div class="stream-header">
                    <span>Stream ${stream.L1}</span>
                    <span class="stream-count">${stream.size}</span>
                </div>
                <div class="stream-keywords">${this.truncate(stream.label, 60)}</div>
            `;
            
            li.addEventListener('click', () => {
                this.selectStream(stream.L1);
            });
            
            streamList.appendChild(li);
        });
    }

    selectStream(streamId) {
        this.currentStream = streamId;
        this.currentL2 = null;
        
        // Update active state
        document.querySelectorAll('.stream-item').forEach(item => {
            item.classList.remove('active');
            if (item.dataset.stream === streamId) {
                item.classList.add('active');
            }
        });
        
        this.renderContent();
    }

    selectL2(l2Path) {
        this.currentL2 = l2Path;
        this.renderContent();
    }

    renderContent() {
        const contentArea = document.getElementById('content-area');
        const breadcrumb = document.getElementById('breadcrumb');
        const title = document.getElementById('content-title');

        if (this.currentView === 'topics') {
            if (this.currentStream === 'all') {
                // Show L1 streams
                title.textContent = 'Research Streams Overview';
                breadcrumb.innerHTML = '<span class="breadcrumb-item active">All Streams</span>';
                contentArea.innerHTML = this.renderL1Topics();
            } else if (!this.currentL2) {
                // Show L2 subtopics for selected L1
                const stream = this.data.level1.find(s => s.L1 === this.currentStream);
                title.textContent = `Stream ${this.currentStream}: ${stream.label}`;
                breadcrumb.innerHTML = `
                    <span class="breadcrumb-item" onclick="app.selectStream('all')">All Streams</span>
                    <span class="breadcrumb-separator">›</span>
                    <span class="breadcrumb-item active">Stream ${this.currentStream}</span>
                `;
                contentArea.innerHTML = this.renderL2Topics();
            } else {
                // Show papers for selected L2
                const l2 = this.data.level2.find(t => t.L2_path === this.currentL2);
                title.textContent = `${l2.L2_path}: ${l2.label}`;
                breadcrumb.innerHTML = `
                    <span class="breadcrumb-item" onclick="app.selectStream('all')">All Streams</span>
                    <span class="breadcrumb-separator">›</span>
                    <span class="breadcrumb-item" onclick="app.selectStream('${this.currentStream}')">Stream ${this.currentStream}</span>
                    <span class="breadcrumb-separator">›</span>
                    <span class="breadcrumb-item active">${l2.L2_path}</span>
                `;
                this.currentView = 'papers'; // Switch to papers view
                contentArea.innerHTML = this.renderPapers();
            }
        } else {
            // Papers view
            title.textContent = this.currentStream === 'all' ? 'All Papers' : `Papers in Stream ${this.currentStream}`;
            contentArea.innerHTML = this.renderPapers();
        }
    }

    renderL1Topics() {
        const topics = this.data.level1;
        
        return `
            <div class="info-box">
                <div class="info-box-title">📊 Level 1: Major Research Streams</div>
                <div class="info-box-content">
                    These 8 high-level streams were discovered using hybrid clustering (text + citation networks).
                    Click any stream to explore its subtopics.
                </div>
            </div>
            <div class="topics-grid">
                ${topics.map(topic => `
                    <div class="topic-card" onclick="app.selectStream('${topic.L1}')">
                        <div class="topic-header">
                            <div class="topic-id">Stream ${topic.L1}</div>
                            <div class="topic-size">${topic.size} papers</div>
                        </div>
                        <div class="topic-keywords">${topic.label}</div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderL2Topics() {
        const topics = this.data.level2.filter(t => String(t.L1) === String(this.currentStream));
        
        if (topics.length === 0) {
            return '<div class="empty-state"><h3>No subtopics found</h3></div>';
        }
        
        return `
            <div class="info-box">
                <div class="info-box-title">🔬 Level 2: Detailed Subtopics</div>
                <div class="info-box-content">
                    Discovered using NMF (Non-negative Matrix Factorization) within Stream ${this.currentStream}.
                    Click any subtopic to view its papers.
                </div>
            </div>
            <div class="topics-grid">
                ${topics.map(topic => `
                    <div class="topic-card" onclick="app.selectL2('${topic.L2_path}')">
                        <div class="topic-header">
                            <div class="topic-id">${topic.L2_path}</div>
                            <div class="topic-size">${topic.size} papers</div>
                        </div>
                        <div class="topic-keywords">${topic.label}</div>
                    </div>
                `).join('')}
            </div>
        `;
    }

    renderPapers() {
        let papers = this.data.papers;

        // Filter by stream
        if (this.currentStream !== 'all') {
            papers = papers.filter(p => String(p.level1_cluster || p.L1) === String(this.currentStream));
        }

        // Filter by L2 if selected
        if (this.currentL2) {
            const [l1, l2] = this.currentL2.split('.');
            papers = papers.filter(p => 
                String(p.level1_cluster || p.L1) === String(l1) && 
                String(p.level2_cluster || p.L2) === String(l2)
            );
        }

        // Apply search filter
        if (this.searchQuery) {
            papers = papers.filter(p => 
                (p.title && p.title.toLowerCase().includes(this.searchQuery)) ||
                (p.L1_label && p.L1_label.toLowerCase().includes(this.searchQuery)) ||
                (p.L2_label && p.L2_label.toLowerCase().includes(this.searchQuery))
            );
        }

        // Apply filter chips
        switch (this.activeFilter) {
            case 'recent':
                papers = papers.filter(p => parseInt(p.year) >= 2020);
                break;
            case 'classics':
                papers = papers.filter(p => parseInt(p.year) < 2010);
                break;
        }

        if (papers.length === 0) {
            return `
                <div class="empty-state">
                    <h3>No papers found</h3>
                    <p>Try adjusting your search or filters</p>
                </div>
            `;
        }

        // Sort by year (descending)
        papers = papers.sort((a, b) => (parseInt(b.year) || 0) - (parseInt(a.year) || 0));

        return `
            <div class="info-box">
                <div class="info-box-title">📄 Papers (${papers.length})</div>
                <div class="info-box-content">
                    Papers are assigned using hybrid clustering. Click "Show details" to see full metadata.
                </div>
            </div>
            <ul class="papers-list">
                ${papers.map((paper, idx) => this.renderPaperItem(paper, idx)).join('')}
            </ul>
        `;
    }

    renderPaperItem(paper, idx) {
        const l1Label = paper.L1_label || paper.level1_label || 'Unknown';
        const l2Label = paper.L2_label || paper.level2_label || 'Unknown';
        const l3Label = paper.L3_label || paper.level3_label || null;
        
        return `
            <li class="paper-item">
                <div class="paper-title">${paper.title || 'Untitled'}</div>
                <div class="paper-meta">
                    <div class="paper-meta-item">
                        📅 ${paper.year || 'N/A'}
                    </div>
                    <div class="paper-meta-item">
                        📚 ${paper.journal || paper.journal_short || 'N/A'}
                    </div>
                    ${paper.doi ? `
                        <div class="paper-meta-item">
                            🔗 <a href="https://doi.org/${paper.doi}" target="_blank" style="color: var(--primary);">DOI</a>
                        </div>
                    ` : ''}
                </div>
                <div class="paper-topics">
                    <div class="paper-topic-tag">Stream ${paper.level1_cluster || paper.L1}: ${this.truncate(l1Label, 40)}</div>
                    <div class="paper-topic-tag">Topic ${paper.level2_cluster || paper.L2}: ${this.truncate(l2Label, 40)}</div>
                    ${l3Label ? `<div class="paper-topic-tag">L3: ${this.truncate(l3Label, 40)}</div>` : ''}
                </div>
                <div class="toggle-details" onclick="this.nextElementSibling.classList.toggle('show')">
                    ▸ Show details
                </div>
                <div class="paper-details">
                    <div class="detail-row">
                        <span class="detail-label">DOI:</span>
                        ${paper.doi ? `<a href="https://doi.org/${paper.doi}" target="_blank">${paper.doi}</a>` : 'N/A'}
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Publication:</span>
                        ${paper.publication_date || 'N/A'}
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Volume/Issue:</span>
                        ${paper.volume ? `Vol. ${paper.volume}` : ''} ${paper.issue ? `Issue ${paper.issue}` : ''}
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">Pages:</span>
                        ${paper.page || 'N/A'}
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">L1 Stream:</span>
                        ${l1Label}
                    </div>
                    <div class="detail-row">
                        <span class="detail-label">L2 Subtopic:</span>
                        ${l2Label}
                    </div>
                    ${l3Label ? `
                    <div class="detail-row">
                        <span class="detail-label">L3 Micro-topic:</span>
                        ${l3Label}
                    </div>
                    ` : ''}
                </div>
            </li>
        `;
    }

    truncate(str, maxLen) {
        if (!str) return '';
        return str.length > maxLen ? str.substring(0, maxLen) + '...' : str;
    }

    showError(message) {
        document.getElementById('content-area').innerHTML = `
            <div class="empty-state">
                <h3>⚠️ Error</h3>
                <p>${message}</p>
            </div>
        `;
    }
}

// Initialize the app when DOM is ready
let app;
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        app = new LiteratureExplorer();
    });
} else {
    app = new LiteratureExplorer();
}
