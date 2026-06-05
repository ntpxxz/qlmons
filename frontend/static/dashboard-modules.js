/**
 * Dashboard Modular Architecture
 * Provides reusable patterns: DataFetcher, Store, EventManager
 * Complements existing dashboard code - use alongside main script
 */

// ============================================================================
// MODULE 1: CORE UTILITIES
// ============================================================================

const DashboardUtils = {
  esc: (str) => {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
  },

  formatTimestamp: (isoString) => {
    if (!isoString) return 'N/A';
    const date = new Date(isoString);
    const hours = String(date.getHours()).padStart(2, '0');
    const mins = String(date.getMinutes()).padStart(2, '0');
    const month = String(date.getMonth() + 1).padStart(2, '0');
    const day = String(date.getDate()).padStart(2, '0');
    return `${hours}:${mins} ${month}/${day}`;
  },

  errorHTML: (msg) =>
    `<div class="text-red" style="text-align:center;padding:20px;font-size:11px;">⚠ ${DashboardUtils.esc(msg)}</div>`,
};

// ============================================================================
// MODULE 2: CENTRALIZED DATA STORE
// ============================================================================

const DashboardStore = {
  data: {
    sessions: [],
    pendingHosts: [],
    whitelist: [],
    blacklist: [],
    auditLogs: [],
    databases: [],
  },

  get(key) {
    return this.data[key] || [];
  },

  set(key, value) {
    this.data[key] = value;
    this.notify(key);
  },

  listeners: {},

  subscribe(key, callback) {
    if (!this.listeners[key]) this.listeners[key] = [];
    this.listeners[key].push(callback);
  },

  notify(key) {
    (this.listeners[key] || []).forEach(cb => cb(this.data[key]));
  },
};

// ============================================================================
// MODULE 3: DATA FETCHER FACTORY
// ============================================================================

function createDataFetcher(config) {
  const { endpoint, storeKey, selector, parser = (d) => d } = config;

  return {
    async load() {
      try {
        const response = await fetch(endpoint);
        const json = await response.json();
        if (!response.ok || !json.success) {
          this.renderError(json.error || 'Failed');
          return null;
        }
        const parsed = parser(json);
        DashboardStore.set(storeKey, parsed);
        return parsed;
      } catch (err) {
        console.error(`Load error (${storeKey}):`, err);
        this.renderError('Connection error');
        return null;
      }
    },

    render(data) {
      const el = document.getElementById(selector);
      if (!el) return;
      data = data || DashboardStore.get(storeKey);
      if (!data || data.length === 0) {
        el.innerHTML = '<div class="text-dim" style="text-align:center;padding:20px;">No data</div>';
        return;
      }
      el.innerHTML = this.renderItems(data);
    },

    renderError(msg) {
      const el = document.getElementById(selector);
      if (el) el.innerHTML = DashboardUtils.errorHTML(msg);
    },

    renderItems(data) { return ''; },

    async refresh() {
      const data = await this.load();
      if (data) this.render(data);
    },
  };
}

// ============================================================================
// MODULE 4: EVENT MANAGER
// ============================================================================

const DashboardEventManager = {
  handlers: {},

  register(action, handler) {
    this.handlers[action] = handler;
  },

  async dispatch(action, payload) {
    const handler = this.handlers[action];
    if (!handler) return console.warn(`No handler: ${action}`);
    return await handler(payload);
  },

  init() {
    document.addEventListener('click', async (e) => {
      const btn = e.target.closest('[data-action]');
      if (!btn) return;
      await this.dispatch(btn.dataset.action, { btn, ...btn.dataset });
    });
  },
};

// ============================================================================
// MODULE 5: VIEW IMPLEMENTATIONS
// ============================================================================

const DatabaseActivityView = createDataFetcher({
  endpoint: '/api/metrics/by-database',
  storeKey: 'databases',
  selector: 'activity-list',
  parser: (json) => json.by_database,
});

DatabaseActivityView.sortBy = 'sessions';

DatabaseActivityView.renderItems = function(databases) {
  const filter = (document.getElementById('activity-filter')?.value || '').toLowerCase();

  let filtered = databases.filter(db =>
    db.database_name.toLowerCase().includes(filter)
  );

  // Apply sorting
  if (this.sortBy === 'sessions') {
    filtered.sort((a, b) => (b.session_count || 0) - (a.session_count || 0));
  } else if (this.sortBy === 'users') {
    filtered.sort((a, b) => (b.unique_users || 0) - (a.unique_users || 0));
  } else if (this.sortBy === 'hosts') {
    filtered.sort((a, b) => (b.unique_hosts || 0) - (a.unique_hosts || 0));
  }
  return databases.map(db => {
    const sessionColor = (db.session_count || 0) > 100 ? 'var(--alert-red)' :
                         (db.session_count || 0) > 50 ? 'var(--warn-yellow)' : 'var(--safe-green)';
    const status = (db.session_count || 0) > 150 ? '⚠ HIGH' :
                   (db.session_count || 0) > 100 ? '⚠ ELEVATED' : '✓ NORMAL';
    const statusColor = (db.session_count || 0) > 150 ? 'var(--alert-red)' :
                       (db.session_count || 0) > 100 ? 'var(--warn-yellow)' : 'var(--safe-green)';

    return `
      <div class="db-activity-card" style="cursor:pointer;" onclick='openDbDetailModal(${JSON.stringify(db.database_name)})'>
        <div style="display:flex; justify-content:space-between; align-items:flex-start; margin-bottom:8px;">
          <div>
            <div style="font-size:12px; font-weight:700; color:var(--primary-cyan);">🗄️ ${DashboardUtils.esc(db.database_name)}</div>
            <div style="font-size:8px; color:var(--text-dim); margin-top:2px;">${db.newest_session ? DashboardUtils.esc(DashboardUtils.formatTimestamp(db.newest_session)) : 'No activity'}</div>
          </div>
          <div style="text-align:right;">
            <div style="font-size:10px; color:${statusColor}; font-weight:700;">${status}</div>
          </div>
        </div>
        <div style="display:grid; grid-template-columns:repeat(3,1fr); gap:6px; font-size:10px;">
          <div style="background:rgba(0,229,255,0.08); padding:6px; border-radius:1px; text-align:center;">
            <div style="color:var(--text-dim); font-size:7px; margin-bottom:2px; text-transform:uppercase;">Sessions</div>
            <div style="color:${sessionColor}; font-weight:bold; font-size:11px;">${db.session_count || 0}</div>
          </div>
          <div style="background:rgba(0,229,255,0.08); padding:6px; border-radius:1px; text-align:center;">
            <div style="color:var(--text-dim); font-size:7px; margin-bottom:2px; text-transform:uppercase;">Users</div>
            <div style="color:var(--safe-green); font-weight:bold; font-size:11px;">${db.unique_users || 0}</div>
          </div>
          <div style="background:rgba(0,229,255,0.08); padding:6px; border-radius:1px; text-align:center;">
            <div style="color:var(--text-dim); font-size:7px; margin-bottom:2px; text-transform:uppercase;">Hosts</div>
            <div style="color:var(--safe-green); font-weight:bold; font-size:11px;">${db.unique_hosts || 0}</div>
          </div>
        </div>
      </div>
    `;
  }).join('');
};

// Register action handlers
DashboardEventManager.register('sort-activity', () => {
  const sorts = ['sessions', 'users', 'hosts'];
  const idx = sorts.indexOf(DatabaseActivityView.sortBy);
  DatabaseActivityView.sortBy = sorts[(idx + 1) % sorts.length];
  DatabaseActivityView.render();
});

DashboardEventManager.register('filter-activity', () => {
  DatabaseActivityView.render();
});

// ============================================================================
// INITIALIZATION
// ============================================================================

function initDashboardModules() {
  console.log('Initializing dashboard modules...');

  DashboardEventManager.init();

  // Load initial data
  DatabaseActivityView.refresh();

  // Auto-refresh every 30 seconds
  setInterval(() => {
    DatabaseActivityView.refresh();
  }, 30000);

  console.log('✓ Dashboard modules ready');
}

// Initialize when DOM is ready
if (document.readyState === 'loading') {
  document.addEventListener('DOMContentLoaded', initDashboardModules);
} else {
  initDashboardModules();
}
