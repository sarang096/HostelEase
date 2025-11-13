const API_URL = '/api';

function showTab(tabName, ev) {
    document.querySelectorAll('.tab-content').forEach(el => el.classList.remove('active'));
    document.querySelectorAll('.tab').forEach(el => el.classList.remove('active'));
    const tabEl = document.getElementById(tabName);
    if (tabEl) tabEl.classList.add('active');
    if (ev && ev.currentTarget) ev.currentTarget.classList.add('active');
    loadTable(tabName).catch(err => console.error(err));
}

async function loadTable(tableName) {
    const res = await fetch(`${API_URL}/${tableName}`, { credentials: 'include' });
    if (res.status === 401) return window.location.href = 'login.html';
    if (!res.ok) throw new Error('Failed to load table: ' + res.status);

    const data = await res.json();
    const table = document.querySelector(`#${tableName}Table`);
    if (!table) return; // nothing to render

    if (!Array.isArray(data) || data.length === 0) {
        table.innerHTML = '<tbody><tr><td>No data</td></tr></tbody>';
        return;
    }

    const headers = Object.keys(data[0]);
    table.innerHTML = `
        <thead><tr>${headers.map(h => `<th>${h}</th>`).join('')}</tr></thead>
        <tbody>${data.map(row => `<tr>${headers.map(h => `<td>${sanitize(row[h])}</td>`).join('')}</tr>`).join('')}</tbody>
    `;
}

function sanitize(v) {
    if (v === null || v === undefined) return '';
    return String(v).replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

// initial load
document.addEventListener('DOMContentLoaded', () => {
    // try to load a default public table
    if (document.getElementById('blockinfoTable')) loadTable('blockinfo').catch(() => {});
});
