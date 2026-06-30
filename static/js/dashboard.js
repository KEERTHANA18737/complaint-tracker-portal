/**
 * dashboard.js – Chart.js dashboard widgets
 * Called from dashboard.html with JSON data injected by the Django view.
 */

const PALETTE = [
  '#1a6fc4','#f0a500','#27ae60','#9b59b6',
  '#e74c3c','#16a085','#e67e22','#2980b9',
];

function initDashboardCharts(
  categoryLabels, categoryCounts,
  monthlyLabels,  monthlyCounts,
  statusLabels,   statusCounts
) {

  // ── Category doughnut ────────────────────────────────────────
  const catCtx = document.getElementById('categoryChart');
  if (catCtx && categoryLabels.length) {
    new Chart(catCtx, {
      type: 'doughnut',
      data: {
        labels:   categoryLabels,
        datasets: [{
          data:            categoryCounts,
          backgroundColor: PALETTE,
          borderWidth:     2,
          borderColor:     '#fff',
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: { position: 'bottom', labels: { font: { size: 11 } } },
        },
        cutout: '60%',
      },
    });
  }

  // ── Monthly bar ──────────────────────────────────────────────
  const monthCtx = document.getElementById('monthlyChart');
  if (monthCtx) {
    new Chart(monthCtx, {
      type: 'bar',
      data: {
        labels:   monthlyLabels,
        datasets: [{
          label:           'Complaints',
          data:            monthlyCounts,
          backgroundColor: 'rgba(26, 111, 196, 0.75)',
          borderColor:     '#1a6fc4',
          borderWidth:     1,
          borderRadius:    6,
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        scales: {
          y: { beginAtZero: true, ticks: { precision: 0 } },
          x: { grid: { display: false } },
        },
        plugins: { legend: { display: false } },
      },
    });
  }

  // ── Status pie ───────────────────────────────────────────────
  const statusCtx = document.getElementById('statusChart');
  if (statusCtx && statusLabels.length) {
    const colours = {
      'Pending':     '#f0a500',
      'Assigned':    '#1a6fc4',
      'In Progress': '#9b59b6',
      'Resolved':    '#27ae60',
      'Closed':      '#6b7a8d',
    };
    new Chart(statusCtx, {
      type: 'pie',
      data: {
        labels:   statusLabels,
        datasets: [{
          data:            statusCounts,
          backgroundColor: statusLabels.map(l => colours[l] || '#ccc'),
          borderWidth:     2,
          borderColor:     '#fff',
        }],
      },
      options: {
        responsive: true,
        maintainAspectRatio: true,
        plugins: {
          legend: { position: 'bottom', labels: { font: { size: 11 } } },
        },
      },
    });
  }
}
