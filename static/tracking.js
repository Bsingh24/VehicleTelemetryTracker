const params = new URLSearchParams(window.location.search);
const pids = (params.get('pids') || '').split(',').filter(Boolean);

const MAX_POINTS = 100;
const charts = {};
const grid = document.getElementById('chartGrid');
const statusEl = document.getElementById('status');

pids.forEach(pid => {
    const card = document.createElement('div');
    card.className = 'chart-card';
    card.innerHTML = `
        <h4>${pid}</h4>
        <div class="latest-value" id="latest-${pid}">--</div>
        <canvas id="chart-${pid}"></canvas>
    `;
    grid.appendChild(card);

    const ctx = document.getElementById(`chart-${pid}`).getContext('2d');
    charts[pid] = new Chart(ctx, {
        type: 'line',
        data: {
            labels: [],
            datasets: [{
                label: pid,
                data: [],
                borderColor: '#0973ff',
                backgroundColor: 'rgba(24, 48, 44, 0.1)',
                borderWidth: 2,
                pointRadius: 0,
                tension: 0.25,
                fill: true
            }]
        },
        options: {
            animation: false,
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                x: { ticks: { maxTicksLimit: 10 } },
                y: {}
            }
        }
    });
});

const ws = new WebSocket(`ws://${window.location.host}/ws/trackpids?pids=${pids.join(',')}`);

ws.onopen = () => {
    statusEl.textContent = "Connected — tracking live";
    statusEl.className = "connected";
};

ws.onclose = () => {
    statusEl.textContent = "Disconnected";
    statusEl.className = "disconnected";
};

ws.onerror = (err) => {
    console.error("WebSocket error:", err);
};

ws.onmessage = (event) => {
    const msg = JSON.parse(event.data); 
    const chart = charts[msg.pid];
    if (!chart) return; 

    chart.data.labels.push(msg.timestamp);
    chart.data.datasets[0].data.push(msg.response);

    if (chart.data.labels.length > MAX_POINTS) {
        chart.data.labels.shift();
        chart.data.datasets[0].data.shift();
    }

    chart.update('none');

    const latestEl = document.getElementById(`latest-${msg.pid}`);
    if (latestEl) latestEl.textContent = msg.value;
};