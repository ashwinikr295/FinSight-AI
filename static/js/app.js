let allMetrics = [];
let activeDocId = null;
let kpiBarChart = null;
let kpiDoughnutChart = null;

document.addEventListener("DOMContentLoaded", () => {
    initTabs();
    initUploadForm();
    initChatForm();
    fetchDashboardMetrics();
});

/* Delete Document Function */
async function deleteDocument(docId, companyName) {
    if (!confirm(`Are you sure you want to delete "${companyName}" from the knowledge base?`)) {
        return;
    }

    try {
        const res = await fetch(`/api/documents/${docId}`, {
            method: "DELETE"
        });
        const data = await res.json();

        if (res.ok) {
            // Remove DOM row if exists
            const row = document.getElementById(`doc-row-${docId}`);
            if (row) row.remove();

            alert(`Document "${companyName}" successfully removed.`);
            
            // Refresh dashboard metrics
            await fetchDashboardMetrics();
        } else {
            alert(`Error: ${data.detail || 'Could not delete document.'}`);
        }
    } catch (err) {
        console.error("Delete error:", err);
        alert("Failed to delete document.");
    }
}

/* Tab Switching */
function initTabs() {
    const navItems = document.querySelectorAll(".nav-item");
    const tabContents = document.querySelectorAll(".tab-content");
    const pageTitle = document.getElementById("page-title");

    const tabTitles = {
        "tab-dashboard": "Executive Financial Dashboard",
        "tab-ingest": "Document Ingestion & Pipeline",
        "tab-chat": "Interactive RAG Investor Assistant",
        "tab-insights": "Risk & Growth Intelligence"
    };

    navItems.forEach(item => {
        item.addEventListener("click", () => {
            const targetTab = item.getAttribute("data-tab");

            navItems.forEach(n => n.classList.remove("active"));
            tabContents.forEach(c => c.classList.remove("active"));

            item.classList.add("active");
            document.getElementById(targetTab).classList.add("active");

            if (pageTitle && tabTitles[targetTab]) {
                pageTitle.textContent = tabTitles[targetTab];
            }
        });
    });

    // Company Selector Event
    const companySelect = document.getElementById("company-select");
    if (companySelect) {
        companySelect.addEventListener("change", (e) => {
            activeDocId = e.target.value;
            renderSelectedDocMetrics(activeDocId);
        });
    }
}

/* Fetch Metrics & Render Dashboard */
async function fetchDashboardMetrics() {
    try {
        const res = await fetch("/api/metrics");
        allMetrics = await res.json();

        if (allMetrics && allMetrics.length > 0) {
            updateCompanySelector();
            activeDocId = allMetrics[0].doc_id;
            renderSelectedDocMetrics(activeDocId);
        } else {
            // Empty state reset
            document.getElementById("company-select").innerHTML = "<option>No documents</option>";
            document.getElementById("kpi-revenue").textContent = "$0";
            document.getElementById("kpi-net-income").textContent = "$0";
            document.getElementById("kpi-operating-income").textContent = "$0";
            document.getElementById("kpi-cash-flow").textContent = "$0";
            document.getElementById("kpi-total-assets").textContent = "$0";
            document.getElementById("kpi-total-liabilities").textContent = "$0";
            document.getElementById("executive-summary-text").textContent = "No financial report uploaded.";
        }
    } catch (err) {
        console.error("Error fetching metrics:", err);
    }
}

function updateCompanySelector() {
    const companySelect = document.getElementById("company-select");
    if (!companySelect) return;

    companySelect.innerHTML = "";
    allMetrics.forEach(m => {
        const opt = document.createElement("option");
        opt.value = m.doc_id;
        opt.textContent = `${m.company_name} (${m.fiscal_year})`;
        companySelect.appendChild(opt);
    });
}

function renderSelectedDocMetrics(docId) {
    const doc = allMetrics.find(m => m.doc_id === docId) || allMetrics[0];
    if (!doc) return;

    // Update KPI Card Values
    document.getElementById("kpi-revenue").textContent = doc.revenue || "N/A";
    document.getElementById("kpi-net-income").textContent = doc.net_income || "N/A";
    document.getElementById("kpi-operating-income").textContent = doc.operating_income || "N/A";
    document.getElementById("kpi-cash-flow").textContent = doc.cash_flow_operating || "N/A";
    document.getElementById("kpi-total-assets").textContent = doc.total_assets || "N/A";
    document.getElementById("kpi-total-liabilities").textContent = doc.total_liabilities || "N/A";

    // Update Executive Summary
    document.getElementById("executive-summary-text").textContent = doc.executive_summary || "Financial report indexed.";

    // Update Risk & Growth Lists
    renderList("risk-factors-list", doc.risk_factors);
    renderList("growth-drivers-list", doc.growth_drivers);

    // Update Charts
    renderCharts(doc);
}

function renderList(elementId, items) {
    const el = document.getElementById(elementId);
    if (!el) return;
    el.innerHTML = "";
    if (items && items.length > 0) {
        items.forEach(item => {
            const li = document.createElement("li");
            li.textContent = item;
            el.appendChild(li);
        });
    } else {
        el.innerHTML = "<li>No details recorded.</li>";
    }
}

/* Render Financial Charts */
function renderCharts(doc) {
    const parseVal = (str) => {
        if (!str) return 0;
        const num = parseFloat(str.replace(/[^0-9.]/g, ''));
        return isNaN(num) ? 0 : num / 1e9; // convert to Billions
    };

    const rev = parseVal(doc.revenue);
    const net = parseVal(doc.net_income);
    const opInc = parseVal(doc.operating_income);
    const cash = parseVal(doc.cash_flow_operating);
    const assets = parseVal(doc.total_assets);
    const liab = parseVal(doc.total_liabilities);

    // 1. Bar Chart
    const ctxBar = document.getElementById("kpiBarChart").getContext("2d");
    if (kpiBarChart) kpiBarChart.destroy();

    kpiBarChart = new Chart(ctxBar, {
        type: 'bar',
        data: {
            labels: ['Revenue', 'Net Income', 'Operating Income', 'Cash Flow'],
            datasets: [{
                label: '$ Billions',
                data: [rev, net, opInc, cash],
                backgroundColor: [
                    '#0284c7',
                    '#059669',
                    '#4338ca',
                    '#2563eb'
                ],
                borderRadius: 6
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: { legend: { display: false } },
            scales: {
                y: { ticks: { color: '#64748b' }, grid: { color: '#e2e8f0' } },
                x: { ticks: { color: '#334155' }, grid: { display: false } }
            }
        }
    });

    // 2. Doughnut Chart (Assets vs Liabilities)
    const ctxDoughnut = document.getElementById("kpiDoughnutChart").getContext("2d");
    if (kpiDoughnutChart) kpiDoughnutChart.destroy();

    kpiDoughnutChart = new Chart(ctxDoughnut, {
        type: 'doughnut',
        data: {
            labels: ['Total Assets ($B)', 'Total Liabilities ($B)'],
            datasets: [{
                data: [assets, liab],
                backgroundColor: ['#7e22ce', '#dc2626'],
                borderWidth: 0
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { labels: { color: '#334155' } }
            }
        }
    });
}

/* Upload Form Handling */
function initUploadForm() {
    const form = document.getElementById("upload-form");
    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("file-input");
    const fileNameBadge = document.getElementById("selected-file-name");
    const progressContainer = document.getElementById("upload-progress-container");
    const progressFill = document.getElementById("progress-fill");
    const progressPercent = document.getElementById("progress-percent");
    const progressStatusText = document.getElementById("progress-status-text");

    const openUploadBtn = document.getElementById("open-upload-btn");
    if (openUploadBtn) {
        openUploadBtn.addEventListener("click", () => {
            document.querySelector('[data-tab="tab-ingest"]').click();
        });
    }

    dropZone.addEventListener("click", () => fileInput.click());

    fileInput.addEventListener("change", () => {
        if (fileInput.files.length > 0) {
            fileNameBadge.textContent = `Selected: ${fileInput.files[0].name}`;
        }
    });

    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.style.borderColor = "#2563eb";
    });

    dropZone.addEventListener("dragleave", () => {
        dropZone.style.borderColor = "#cbd5e1";
    });

    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.style.borderColor = "#cbd5e1";
        if (e.dataTransfer.files.length > 0) {
            fileInput.files = e.dataTransfer.files;
            fileNameBadge.textContent = `Selected: ${fileInput.files[0].name}`;
        }
    });

    form.addEventListener("submit", async (e) => {
        e.preventDefault();
        if (!fileInput.files.length) return alert("Please select a file.");

        const formData = new FormData();
        formData.append("file", fileInput.files[0]);
        formData.append("company_name", document.getElementById("input-company").value);
        formData.append("fiscal_year", document.getElementById("input-year").value);

        progressContainer.classList.remove("hidden");
        progressFill.style.width = "30%";
        progressPercent.textContent = "30%";
        progressStatusText.textContent = "Converting PDF to Markdown...";

        try {
            setTimeout(() => {
                progressFill.style.width = "70%";
                progressPercent.textContent = "70%";
                progressStatusText.textContent = "Running Semantic Chunking & 8-KPI Extractor...";
            }, 800);

            const res = await fetch("/api/upload", {
                method: "POST",
                body: formData
            });
            const data = await res.json();

            progressFill.style.width = "100%";
            progressPercent.textContent = "100%";
            progressStatusText.textContent = "Document Processed & Indexed!";

            setTimeout(() => {
                alert(`Successfully ingested report for ${data.company_name} (${data.fiscal_year})!`);
                progressContainer.classList.add("hidden");
                form.reset();
                fileNameBadge.textContent = "";
                fetchDashboardMetrics();
                // Reload window to refresh Jinja list cleanly
                window.location.reload();
            }, 600);

        } catch (err) {
            console.error("Upload failed:", err);
            alert("Error uploading document.");
            progressContainer.classList.add("hidden");
        }
    });
}

/* Chat Form & Sample Chips Handling */
function initChatForm() {
    const form = document.getElementById("chat-form");
    const input = document.getElementById("chat-input");
    const chatContainer = document.getElementById("chat-messages");

    // Sample Question Chips
    document.querySelectorAll(".sample-chip").forEach(chip => {
        chip.addEventListener("click", () => {
            const query = chip.getAttribute("data-query");
            input.value = query;
            submitQuery(query);
        });
    });

    form.addEventListener("submit", (e) => {
        e.preventDefault();
        const query = input.value.trim();
        if (!query) return;
        submitQuery(query);
    });

    async function submitQuery(query) {
        input.value = "";
        appendUserMessage(query);

        const loadingMsgId = appendLoadingMessage();

        try {
            const selectedCompOption = document.getElementById("company-select");
            let companyFilter = null;
            if (selectedCompOption && selectedCompOption.options.length > 0) {
                const text = selectedCompOption.options[selectedCompOption.selectedIndex].text;
                companyFilter = text.split(" (")[0];
            }

            const res = await fetch("/api/chat", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ query: query, company_name: companyFilter })
            });
            const data = await res.json();

            removeLoadingMessage(loadingMsgId);
            appendSystemMessage(data.answer, data.citations);

        } catch (err) {
            console.error("Chat error:", err);
            removeLoadingMessage(loadingMsgId);
            appendSystemMessage("Sorry, an error occurred while processing your query.", []);
        }
    }

    function appendUserMessage(text) {
        const div = document.createElement("div");
        div.className = "message user-msg";
        div.innerHTML = `
            <div class="avatar"><i class="fa-solid fa-user"></i></div>
            <div class="msg-body"><p>${text}</p></div>
        `;
        chatContainer.appendChild(div);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }

    function appendLoadingMessage() {
        const id = "loading-" + Date.now();
        const div = document.createElement("div");
        div.id = id;
        div.className = "message system-msg";
        div.innerHTML = `
            <div class="avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="msg-body"><p><i class="fa-solid fa-spinner fa-spin"></i> Retrieving context chunks & generating grounded response...</p></div>
        `;
        chatContainer.appendChild(div);
        chatContainer.scrollTop = chatContainer.scrollHeight;
        return id;
    }

    function removeLoadingMessage(id) {
        const el = document.getElementById(id);
        if (el) el.remove();
    }

    function appendSystemMessage(answer, citations) {
        const div = document.createElement("div");
        div.className = "message system-msg";

        let citationsHTML = "";
        if (citations && citations.length > 0) {
            citationsHTML = `
                <div class="citations-box">
                    <span class="citation-title"><i class="fa-solid fa-book-bookmark"></i> RAG Grounded Sources (${citations.length}):</span>
                    ${citations.map(c => `
                        <div class="citation-badge">
                            <strong>[Source ${c.id}] ${c.company_name} (${c.fiscal_year}) - ${c.section_title}</strong> (Match: ${c.confidence})<br>
                            <em>"${c.snippet}"</em>
                        </div>
                    `).join('')}
                </div>
            `;
        }

        div.innerHTML = `
            <div class="avatar"><i class="fa-solid fa-robot"></i></div>
            <div class="msg-body">
                <p>${answer}</p>
                ${citationsHTML}
            </div>
        `;
        chatContainer.appendChild(div);
        chatContainer.scrollTop = chatContainer.scrollHeight;
    }
}
