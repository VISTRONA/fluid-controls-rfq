/**
 * RFQ Traceability Management System - Dashboard Charts
 */

let rfqTrendChart = null;

document.addEventListener('DOMContentLoaded', () => {
  initTypeChart();
  initTrendChart('monthly');
  initEmployeePerformanceChart();
  initReceivedVsCompletedChart();
  initStatusDistributionChart();
  initSlaPerformanceChart();
});

// Chart 1: RFQs by Type
async function initTypeChart() {
  const canvas = document.getElementById('chartRfqType');
  if (!canvas) return;

  try {
    const res = await fetch('/api/dashboard/type-distribution');
    const data = await res.json();

    new Chart(canvas, {
      type: 'bar',
      data: {
        labels: data.labels,
        datasets: [{
          label: 'Total RFQs',
          data: data.data,
          backgroundColor: [
            'rgba(37, 99, 235, 0.85)',
            'rgba(16, 185, 129, 0.85)',
            'rgba(245, 158, 11, 0.85)',
            'rgba(139, 92, 246, 0.85)'
          ],
          borderColor: [
            '#2563eb',
            '#10b981',
            '#f59e0b',
            '#8b5cf6'
          ],
          borderWidth: 1,
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            padding: 10,
            cornerRadius: 8
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { precision: 0 }
          },
          x: {
            grid: { display: false }
          }
        }
      }
    });
  } catch (err) {
    console.error('Error loading type distribution chart:', err);
  }
}

// Chart 2: RFQs Over Time (Line chart with period toggle)
async function initTrendChart(period = 'monthly') {
  const canvas = document.getElementById('chartRfqTrend');
  if (!canvas) return;

  try {
    const res = await fetch(`/api/dashboard/rfq-trend?period=${period}`);
    const data = await res.json();

    if (rfqTrendChart) {
      rfqTrendChart.destroy();
    }

    const ctx = canvas.getContext('2d');
    const gradient = ctx.createLinearGradient(0, 0, 0, 240);
    gradient.addColorStop(0, 'rgba(37, 99, 235, 0.35)');
    gradient.addColorStop(1, 'rgba(37, 99, 235, 0.02)');

    rfqTrendChart = new Chart(canvas, {
      type: 'line',
      data: {
        labels: data.labels,
        datasets: [{
          label: 'RFQs Influx',
          data: data.datasets[0].data,
          borderColor: '#2563eb',
          backgroundColor: gradient,
          borderWidth: 2.5,
          pointBackgroundColor: '#2563eb',
          pointBorderColor: '#ffffff',
          pointBorderWidth: 2,
          pointRadius: 4.5,
          pointHoverRadius: 7,
          tension: 0.38,
          fill: true
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: { display: false },
          tooltip: {
            padding: 10,
            cornerRadius: 8
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { precision: 0 }
          },
          x: {
            grid: { color: 'rgba(226, 232, 240, 0.6)' }
          }
        }
      }
    });
  } catch (err) {
    console.error('Error loading RFQ trend chart:', err);
  }
}

function loadTrendData(period, btn) {
  if (btn && btn.parentElement) {
    const buttons = btn.parentElement.querySelectorAll('button');
    buttons.forEach(b => b.classList.remove('active'));
    btn.classList.add('active');
  }
  initTrendChart(period);
}

// Chart 3: Sales / Employee Performance (Horizontal Bar Chart)
async function initEmployeePerformanceChart() {
  const canvas = document.getElementById('chartEmployeePerf');
  if (!canvas) return;

  try {
    const res = await fetch('/api/dashboard/employee-performance');
    const data = await res.json();

    new Chart(canvas, {
      type: 'bar',
      data: {
        labels: data.labels,
        datasets: [
          {
            label: 'Total Assigned',
            data: data.totals,
            backgroundColor: 'rgba(37, 99, 235, 0.8)',
            borderRadius: 4
          },
          {
            label: 'Completed/Won',
            data: data.won,
            backgroundColor: 'rgba(16, 185, 129, 0.85)',
            borderRadius: 4
          }
        ]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: { boxWidth: 12, font: { size: 11 } }
          }
        },
        scales: {
          x: {
            beginAtZero: true,
            ticks: { precision: 0 }
          }
        }
      }
    });
  } catch (err) {
    console.error('Error loading employee performance chart:', err);
  }
}

// Chart 4: Received vs Completion
async function initReceivedVsCompletedChart() {
  const canvas = document.getElementById('chartReceivedVsCompleted');
  if (!canvas) return;

  try {
    const res = await fetch('/api/dashboard/received-vs-completed');
    const data = await res.json();

    new Chart(canvas, {
      type: 'line',
      data: {
        labels: data.labels,
        datasets: [
          {
            label: 'RFQs Received',
            data: data.received,
            borderColor: '#3b82f6',
            backgroundColor: 'rgba(59, 130, 246, 0.1)',
            tension: 0.3,
            fill: false,
            borderWidth: 2,
            pointRadius: 4
          },
          {
            label: 'Orders Closed/Won',
            data: data.completed,
            borderColor: '#10b981',
            backgroundColor: 'rgba(16, 185, 129, 0.1)',
            tension: 0.3,
            fill: false,
            borderWidth: 2,
            pointRadius: 4
          }
        ]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: 'top',
            labels: { boxWidth: 12, font: { size: 11 } }
          }
        },
        scales: {
          y: {
            beginAtZero: true,
            ticks: { precision: 0 }
          }
        }
      }
    });
  } catch (err) {
    console.error('Error loading received vs completed chart:', err);
  }
}

// Chart 5: Status Distribution (Doughnut Chart)
async function initStatusDistributionChart() {
  const canvas = document.getElementById('chartStatusDist');
  if (!canvas) return;

  try {
    const res = await fetch('/api/dashboard/status-distribution');
    const data = await res.json();

    new Chart(canvas, {
      type: 'doughnut',
      data: {
        labels: data.labels,
        datasets: [{
          data: data.data,
          backgroundColor: data.colors,
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '68%',
        plugins: {
          legend: {
            position: 'right',
            labels: {
              boxWidth: 12,
              font: { size: 11, family: 'Plus Jakarta Sans' },
              padding: 10
            }
          }
        }
      }
    });
  } catch (err) {
    console.error('Error loading status distribution chart:', err);
  }
}

// Chart 6: SLA Performance Breakdown
async function initSlaPerformanceChart() {
  const canvas = document.getElementById('chartSlaPerf');
  if (!canvas) return;

  try {
    const res = await fetch('/api/dashboard/sla-performance');
    const data = await res.json();

    new Chart(canvas, {
      type: 'doughnut',
      data: {
        labels: data.labels,
        datasets: [{
          data: data.data,
          backgroundColor: data.colors,
          borderWidth: 2,
          borderColor: '#ffffff'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '68%',
        plugins: {
          legend: {
            position: 'right',
            labels: {
              boxWidth: 12,
              font: { size: 11, family: 'Plus Jakarta Sans' },
              padding: 12
            }
          }
        }
      }
    });
  } catch (err) {
    console.error('Error loading SLA performance chart:', err);
  }
}
