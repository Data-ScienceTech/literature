// Dashboard Data Module
// This file contains the processed data for the IS Research Dashboard

// Sample data structure - this will be populated with actual analysis results
const dashboardData = {
    papers: [],
    streams: [],
    stats: {
        totalPapers: 6556,
        totalStreams: 28,
        totalCitations: 907900,
        abstractCoverage: 100,
        yearsAnalyzed: 25,
        journalsAnalyzed: 6
    },
    journals: [
        { name: "Information Systems Research", papers: 1245, coverage: 89 },
        { name: "MIS Quarterly", papers: 1156, coverage: 85 },
        { name: "Journal of the Association for Information Systems", papers: 987, coverage: 78 },
        { name: "Information Systems Journal", papers: 1089, coverage: 82 },
        { name: "Journal of Management Information Systems", papers: 1234, coverage: 88 },
        { name: "Journal of Information Technology", papers: 845, coverage: 81 }
    ],
    timeline: [
        { year: 2000, papers: 145 },
        { year: 2001, papers: 167 },
        { year: 2002, papers: 189 },
        { year: 2003, papers: 201 },
        { year: 2004, papers: 234 },
        { year: 2005, papers: 267 },
        { year: 2006, papers: 289 },
        { year: 2007, papers: 312 },
        { year: 2008, papers: 298 },
        { year: 2009, papers: 276 },
        { year: 2010, papers: 289 },
        { year: 2011, papers: 301 },
        { year: 2012, papers: 324 },
        { year: 2013, papers: 345 },
        { year: 2014, papers: 367 },
        { year: 2015, papers: 389 },
        { year: 2016, papers: 401 },
        { year: 2017, papers: 423 },
        { year: 2018, papers: 445 },
        { year: 2019, papers: 467 },
        { year: 2020, papers: 489 },
        { year: 2021, papers: 512 },
        { year: 2022, papers: 498 },
        { year: 2023, papers: 445 },
        { year: 2024, papers: 389 },
        { year: 2025, papers: 123 }
    ]
};

// Sample research streams data
dashboardData.streams = [
    {
        id: 0,
        title: "Technology Acceptance and User Behavior",
        size: 549,
        avgCitations: 287,
        totalCitations: 157563,
        topTerms: ["technology acceptance", "user behavior", "tam", "adoption", "perceived usefulness"],
        yearRange: "2000-2025",
        recentActivity: 0.34,
        description: "Research focusing on how users adopt and accept new technologies, including TAM and UTAUT models.",
        samplePapers: [
            {
                title: "Understanding Information Technology Usage: A Test of Competing Models",
                authors: "Straub, D., Limayem, M., Karahanna-Evaristo, E.",
                year: 2005,
                journal: "Information Systems Research",
                citations: 1245,
                doi: "10.1287/isre.16.4.389.61779"
            },
            {
                title: "Technology Acceptance Model: A Decade of Empirical Research",
                authors: "Turner, M., Kitchenham, B., Brereton, P.",
                year: 2010,
                journal: "MIS Quarterly",
                citations: 892,
                doi: "10.2307/25148640"
            }
        ]
    },
    {
        id: 1,
        title: "Knowledge Management and Organizational Learning",
        size: 445,
        avgCitations: 234,
        totalCitations: 104130,
        topTerms: ["knowledge management", "organizational learning", "knowledge sharing", "tacit knowledge", "innovation"],
        yearRange: "2000-2024",
        recentActivity: 0.28,
        description: "Studies on how organizations create, share, and leverage knowledge for competitive advantage.",
        samplePapers: [
            {
                title: "Knowledge Management and Innovation: Networks and Networking",
                authors: "Swan, J., Newell, S., Scarbrough, H.",
                year: 2010,
                journal: "Journal of Knowledge Management",
                citations: 567,
                doi: "10.1108/13673271011032409"
            }
        ]
    },
    {
        id: 2,
        title: "Digital Platforms and Ecosystems",
        size: 387,
        avgCitations: 198,
        totalCitations: 76626,
        topTerms: ["digital platforms", "platform ecosystems", "network effects", "multi-sided markets", "digital transformation"],
        yearRange: "2005-2025",
        recentActivity: 0.67,
        description: "Research on digital platform business models, ecosystem dynamics, and platform strategies.",
        samplePapers: []
    },
    {
        id: 3,
        title: "Cybersecurity and Risk Management",
        size: 298,
        avgCitations: 156,
        totalCitations: 46488,
        topTerms: ["cybersecurity", "information security", "risk management", "privacy", "data protection"],
        yearRange: "2002-2025",
        recentActivity: 0.72,
        description: "Studies on information security threats, risk assessment, and cybersecurity management practices.",
        samplePapers: []
    },
    {
        id: 4,
        title: "AI and Machine Learning Applications",
        size: 234,
        avgCitations: 145,
        totalCitations: 33930,
        topTerms: ["artificial intelligence", "machine learning", "predictive analytics", "automation", "decision support"],
        yearRange: "2010-2025",
        recentActivity: 0.89,
        description: "Research on AI/ML applications in business contexts and decision-making processes.",
        samplePapers: []
    },
    {
        id: 5,
        title: "E-commerce and Digital Markets",
        size: 423,
        avgCitations: 267,
        totalCitations: 112941,
        topTerms: ["e-commerce", "online markets", "digital business", "electronic markets", "consumer behavior"],
        yearRange: "2000-2024",
        recentActivity: 0.31,
        description: "Studies on electronic commerce, online consumer behavior, and digital market mechanisms.",
        samplePapers: []
    }
];

// Function to load actual data from CSV files
async function loadActualData() {
    try {
        // This would load the actual analysis results
        // For now, we'll use the sample data above
        console.log("Loading dashboard data...");
        return dashboardData;
    } catch (error) {
        console.error("Error loading data:", error);
        return dashboardData; // Fallback to sample data
    }
}

// Initialize data when the script loads
let currentData = dashboardData;