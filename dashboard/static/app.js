// State Management
let currentFilter = 'all';
let draftsData = [];

// Secure Fetch Wrapper to handle auto-redirection on expired sessions (401)
async function secureFetch(url, options = {}) {
    const response = await fetch(url, options);
    if (response.status === 401) {
        window.location.href = '/login';
        return null;
    }
    return response;
}

// Initialize Page
document.addEventListener('DOMContentLoaded', () => {
    fetchStatus();
    fetchQueue();
    
    // Auto refresh status and queue every 10 seconds
    setInterval(() => {
        fetchStatus();
    }, 10000);

    // Bind Sandbox Form
    const sandboxForm = document.getElementById('sandbox-form');
    sandboxForm.addEventListener('submit', handleSandboxSubmit);
});

// Toast Notifications Helper
function showToast(message, type = 'info') {
    const container = document.getElementById('toast-container');
    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    
    // Icon selection
    let iconName = 'info';
    if (type === 'success') iconName = 'check_circle';
    if (type === 'error') iconName = 'error';
    
    toast.innerHTML = `
        <span class="material-symbols-outlined">${iconName}</span>
        <span>${message}</span>
    `;
    
    container.appendChild(toast);
    
    // Animate in
    setTimeout(() => toast.classList.add('show'), 10);
    
    // Remove after 4 seconds
    setTimeout(() => {
        toast.classList.remove('show');
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// API: Fetch Bot Statuses
async function fetchStatus() {
    try {
        const response = await secureFetch('/api/status');
        const data = await response.json();
        
        updateBotCard('linkedin', data.linkedin);
        updateBotCard('blog', data.blog);
    } catch (error) {
        console.error('Failed to fetch bot statuses:', error);
    }
}

// UI: Helper to update card details
function updateBotCard(platform, statusObj) {
    const card = document.getElementById(`card-${platform}`);
    if (!card) return;
    
    const statusText = card.querySelector('.bot-status');
    const statusDot = card.querySelector('.bot-status-dot') || document.createElement('span');
    
    statusText.textContent = statusObj.status;
    
    // Update color based on configuration
    if (statusObj.status.includes('Ready') || statusObj.status.includes('Active')) {
        statusText.style.color = 'var(--color-success)';
    } else if (statusObj.status.includes('Mock') || statusObj.status.includes('Login')) {
        statusText.style.color = 'var(--color-warning)';
    } else {
        statusText.style.color = 'var(--color-error)';
    }
}

// API: Fetch Review Queue
async function fetchQueue() {
    const container = document.getElementById('queue-container');
    
    try {
        const response = await secureFetch('/api/queue');
        const data = await response.json();
        draftsData = data.drafts || [];
        renderQueue();
    } catch (error) {
        console.error('Failed to fetch review queue:', error);
        showToast('Failed to load review queue.', 'error');
    }
}

// UI: Render Queue Items with Filters
function renderQueue() {
    const container = document.getElementById('queue-container');
    container.innerHTML = '';
    
    const filteredDrafts = draftsData.filter(draft => {
        if (currentFilter === 'all') return true;
        return draft.platform.toLowerCase() === currentFilter.toLowerCase();
    });
    
    if (filteredDrafts.length === 0) {
        container.innerHTML = `
            <div class="empty-state">
                <span class="material-symbols-outlined empty-icon">mark_chat_read</span>
                <h3>No pending drafts found</h3>
                <p>Select another category or click "Generate Drafts" to fetch fresh candidates.</p>
            </div>
        `;
        return;
    }
    
    filteredDrafts.forEach(draft => {
        const card = document.createElement('div');
        card.className = 'queue-card';
        card.dataset.id = draft.id;
        
        // Format timestamp
        const date = new Date(draft.created_at);
        const formattedDate = date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' }) + ' - ' + date.toLocaleDateString();
        
        card.innerHTML = `
            <div class="queue-card-meta">
                <span class="platform-badge badge-${draft.platform}">
                    <span class="material-symbols-outlined" style="font-size: 0.8rem;">tag</span>
                    ${draft.platform.toUpperCase()}
                </span>
                <span class="card-timestamp">${formattedDate}</span>
            </div>
            
            <div class="card-title">${draft.title}</div>
            <a href="${draft.url}" target="_blank" class="card-link">
                <span class="material-symbols-outlined" style="font-size: 0.8rem;">open_in_new</span>
                View Original Post (by ${draft.author})
            </a>
            
            <div class="card-content">${draft.content}</div>
            
            <div class="card-ai-draft">
                <div class="ai-header">
                    <span class="material-symbols-outlined">auto_awesome</span>
                    <span>AI Suggested Reply</span>
                </div>
                <textarea class="draft-textarea" id="textarea-${draft.id}">${draft.suggested_comment}</textarea>
            </div>
            
            <div class="card-actions">
                <button class="btn btn-danger" onclick="rejectDraft('${draft.id}')">
                    <span class="material-symbols-outlined" style="font-size: 0.9rem;">delete</span> Reject
                </button>
                <button class="btn btn-accent" onclick="approveDraft('${draft.id}')" id="btn-approve-${draft.id}">
                    <span class="material-symbols-outlined" style="font-size: 0.9rem;">send</span> Approve & Post
                </button>
            </div>
        `;
        
        container.appendChild(card);
    });
}

// UI: Filter queue platform
function filterQueue(platform) {
    currentFilter = platform;
    
    // Toggle active filter button class
    const filterButtons = document.querySelectorAll('.filter-btn');
    filterButtons.forEach(btn => {
        btn.classList.remove('active');
        if (btn.textContent.toLowerCase().includes(platform.toLowerCase()) || 
            (platform === 'all' && btn.textContent.toLowerCase().includes('all'))) {
            btn.classList.add('active');
        }
    });
    
    renderQueue();
}

// API: Approve and Post
async function approveDraft(draftId) {
    const btn = document.getElementById(`btn-approve-${draftId}`);
    const textarea = document.getElementById(`textarea-${draftId}`);
    const comment = textarea.value.trim();
    
    if (!comment) {
        showToast('Comment cannot be empty!', 'error');
        return;
    }
    
    btn.disabled = true;
    btn.textContent = 'Posting...';
    
    try {
        const response = await secureFetch(`/api/queue/approve/${draftId}`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ approved_comment: comment })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Comment posted successfully!', 'success');
            // Remove draft from local data
            draftsData = draftsData.filter(d => d.id !== draftId);
            renderQueue();
            
            // Print status to terminal
            printTerminalLog(`[SUCCESS] Comment posted to platform successfully.\nResponse: ${data.info || 'OK'}`);
        } else {
            throw new Error(data.detail || 'Failed to post comment.');
        }
    } catch (error) {
        console.error('Approve failed:', error);
        showToast(error.message, 'error');
        btn.disabled = false;
        btn.innerHTML = '<span class="material-symbols-outlined" style="font-size: 0.9rem;">send</span> Approve & Post';
        printTerminalLog(`[ERROR] Failed to post draft:\n${error.message}`);
    }
}

// API: Reject Draft
async function rejectDraft(draftId) {
    try {
        const response = await secureFetch(`/api/queue/reject/${draftId}`, {
            method: 'POST'
        });
        
        if (response.ok) {
            showToast('Draft removed from queue.', 'info');
            draftsData = draftsData.filter(d => d.id !== draftId);
            renderQueue();
        } else {
            const data = await response.json();
            throw new Error(data.detail || 'Failed to reject draft.');
        }
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// API: Generate New Drafts
async function generateDrafts() {
    showToast('Scanning platforms & generating replies...', 'info');
    
    try {
        const response = await secureFetch('/api/queue/generate', {
            method: 'POST'
        });
        const data = await response.json();
        
        if (response.ok) {
            showToast(data.message, 'success');
            fetchQueue();
        } else {
            throw new Error(data.detail || 'Failed to scan platforms.');
        }
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// API: Trigger Background Bots
async function triggerBot(botName) {
    showToast(`Triggering ${botName.toUpperCase()} bot in background...`, 'info');
    
    try {
        const response = await secureFetch(`/api/trigger/${botName}`, {
            method: 'POST'
        });
        const data = await response.json();
        
        if (response.ok) {
            showToast(data.message, 'success');
            printTerminalLog(`[SYSTEM] Triggered background execution for bot: ${botName}`);
        } else {
            throw new Error(data.detail || 'Failed to trigger.');
        }
    } catch (error) {
        showToast(error.message, 'error');
    }
}

// API: View Logs
async function viewLogs(botName) {
    const terminalTitle = document.getElementById('log-viewer-title');
    terminalTitle.textContent = `${botName.toUpperCase()} Log Monitor / State`;
    
    printTerminalLog(`Fetching logs for ${botName}...`);
    
    try {
        const response = await secureFetch(`/api/logs/${botName}`);
        const data = await response.json();
        printTerminalLog(data.logs);
    } catch (error) {
        printTerminalLog(`[ERROR] Failed to fetch logs for ${botName}: ${error}`);
    }
}

// API: Handle Sandbox Manual Draft Submission
async function handleSandboxSubmit(e) {
    e.preventDefault();
    
    const platform = document.getElementById('sandbox-platform').value;
    const url = document.getElementById('sandbox-url').value.trim();
    const submitBtn = e.target.querySelector('button[type="submit"]');
    
    if (!url) return;
    
    submitBtn.disabled = true;
    submitBtn.textContent = 'Generating...';
    showToast('Generating draft sandbox...', 'info');
    
    try {
        const response = await secureFetch('/api/sandbox/draft', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ platform, url })
        });
        
        const data = await response.json();
        
        if (response.ok) {
            showToast('Draft added to top of queue!', 'success');
            document.getElementById('sandbox-url').value = '';
            
            // Reload and focus queue
            fetchQueue();
            
            // Scroll to queue
            document.querySelector('.review-queue-panel').scrollIntoView({ behavior: 'smooth' });
        } else {
            throw new Error(data.detail || 'Sandbox generation failed.');
        }
    } catch (error) {
        showToast(error.message, 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<span class="material-symbols-outlined">smart_toy</span> Generate AI Draft';
    }
}

// UI: Helper to print log messages inside terminal simulation
function printTerminalLog(text) {
    const logOutput = document.getElementById('log-output');
    logOutput.textContent = text;
    
    // Auto-scroll to bottom
    const terminal = logOutput.parentElement;
    terminal.scrollTop = terminal.scrollHeight;
}
