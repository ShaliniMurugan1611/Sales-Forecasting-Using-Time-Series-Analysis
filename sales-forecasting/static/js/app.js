// Sales Forecasting Dashboard JavaScript
let currentCharts = {};

function showAlert(message, type = 'danger') {
    const alertContainer = document.getElementById('alertContainer');
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show`;
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    alertContainer.innerHTML = '';
    alertContainer.appendChild(alert);
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

function showLoading(button) {
    const originalText = button.innerHTML;
    button.disabled = true;
    button.innerHTML = '<span class="spinner-border spinner-border-sm"></span> Loading...';
    return originalText;
}

function hideLoading(button, originalText) {
    button.disabled = false;
    button.innerHTML = originalText;
}

// Navigation
document.querySelectorAll('.nav-link').forEach(link => {
    link.addEventListener('click', function(e) {
        e.preventDefault();
        document.querySelectorAll('.nav-link').forEach(l => l.classList.remove('active'));
        this.classList.add('active');
        
        document.querySelectorAll('.page-content').forEach(p => p.style.display = 'none');
        const page = this.getAttribute('data-page');
        document.getElementById('page-' + page).style.display = 'block';
        document.getElementById('pageTitle').textContent = this.textContent.trim();
        
        if (page === 'overview') loadOverview();
        else if (page === 'analytics') loadAnalytics();
        else if (page === 'forecasting') loadForecastingOptions();
        else if (page === 'history') loadHistory();
        else if (page === 'dataset') loadDatasetInfo();
    });
});

// Refresh button
document.getElementById('refreshBtn').addEventListener('click', function() {
    const activePage = document.querySelector('.nav-link.active').getAttribute('data-page');
    if (activePage === 'overview') loadOverview();
    else if (activePage === 'analytics') loadAnalytics();
    else if (activePage === 'forecasting') loadForecastingOptions();
    else if (activePage === 'history') loadHistory();
    else if (activePage === 'dataset') loadDatasetInfo();
});

// Load Overview
function loadOverview() {
    fetch('/api/overview')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const d = data.data;
                document.getElementById('kpi-revenue').textContent = '$' + d.kpis.total_revenue.toLocaleString();
                document.getElementById('kpi-orders').textContent = d.kpis.total_orders;
                document.getElementById('kpi-avg').textContent = '$' + d.kpis.avg_daily_sales.toFixed(2);
                document.getElementById('kpi-best').textContent = d.kpis.best_selling_product;
                
                // Clear existing charts
                Object.values(currentCharts).forEach(chart => {
                    if (chart) chart.destroy();
                });
                currentCharts = {};
                
                // Historical chart
                const histCtx = document.getElementById('historicalChart').getContext('2d');
                currentCharts.historical = new Chart(histCtx, {
                    type: 'line',
                    data: {
                        labels: d.historical_chart.slice(-60).map(x => x.date),
                        datasets: [{
                            label: 'Daily Sales',
                            data: d.historical_chart.slice(-60).map(x => x.sales),
                            borderColor: '#3498db',
                            tension: 0.1,
                            fill: false
                        }]
                    },
                    options: {
                        responsive: true,
                        scales: {
                            y: {
                                beginAtZero: true
                            }
                        }
                    }
                });
                
                // Product chart
                const prodCtx = document.getElementById('productChart').getContext('2d');
                currentCharts.product = new Chart(prodCtx, {
                    type: 'bar',
                    data: {
                        labels: d.product_chart.map(x => x.product),
                        datasets: [{
                            label: 'Sales',
                            data: d.product_chart.map(x => x.sales),
                            backgroundColor: '#2ecc71'
                        }]
                    },
                    options: {
                        responsive: true,
                        indexAxis: 'y'
                    }
                });
                
                // Monthly chart
                const monthCtx = document.getElementById('monthlyChart').getContext('2d');
                currentCharts.monthly = new Chart(monthCtx, {
                    type: 'bar',
                    data: {
                        labels: d.monthly_chart.map(x => x.month),
                        datasets: [{
                            label: 'Monthly Sales',
                            data: d.monthly_chart.map(x => x.sales),
                            backgroundColor: '#e74c3c'
                        }]
                    },
                    options: {
                        responsive: true
                    }
                });
                
                // Load insights
                fetch('/api/analytics')
                    .then(r => r.json())
                    .then(ad => {
                        if (ad.success) {
                            const insightsList = document.getElementById('insightsList');
                            insightsList.innerHTML = '';
                            ad.data.insights.forEach(insight => {
                                const li = document.createElement('li');
                                li.className = 'list-group-item';
                                li.innerHTML = '<i class="bi bi-lightbulb text-warning"></i> ' + insight;
                                insightsList.appendChild(li);
                            });
                        }
                    });
            } else {
                showAlert(data.error);
            }
        })
        .catch(err => showAlert('Error loading overview: ' + err));
}

// Load Analytics
function loadAnalytics() {
    fetch('/api/analytics')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const d = data.data;
                document.getElementById('trendStatus').textContent = d.trend;
                
                Object.values(currentCharts).forEach(chart => {
                    if (chart && chart.canvas && chart.canvas.id.includes('dow') || 
                        chart.canvas.id.includes('category') || chart.canvas.id.includes('region')) {
                        chart.destroy();
                    }
                });
                
                // Day of week chart
                const dowCtx = document.getElementById('dowChart').getContext('2d');
                currentCharts.dow = new Chart(dowCtx, {
                    type: 'bar',
                    data: {
                        labels: d.day_of_week_chart.map(x => x.day),
                        datasets: [{
                            label: 'Sales',
                            data: d.day_of_week_chart.map(x => x.sales),
                            backgroundColor: '#9b59b6'
                        }]
                    },
                    options: { responsive: true }
                });
                
                // Category chart
                const catCtx = document.getElementById('categoryChart').getContext('2d');
                currentCharts.category = new Chart(catCtx, {
                    type: 'pie',
                    data: {
                        labels: d.category_chart.map(x => x.category),
                        datasets: [{
                            data: d.category_chart.map(x => x.sales),
                            backgroundColor: ['#3498db', '#2ecc71', '#e74c3c', '#f39c12', '#9b59b6']
                        }]
                    },
                    options: { responsive: true }
                });
                
                // Region chart
                const regCtx = document.getElementById('regionChart').getContext('2d');
                currentCharts.region = new Chart(regCtx, {
                    type: 'doughnut',
                    data: {
                        labels: d.region_chart.map(x => x.region),
                        datasets: [{
                            data: d.region_chart.map(x => x.sales),
                            backgroundColor: ['#1abc9c', '#34495e', '#e67e22', '#c0392b', '#8e44ad']
                        }]
                    },
                    options: { responsive: true }
                });
                
                // Analytics insights
                const insightsDiv = document.getElementById('analyticsInsights');
                insightsDiv.innerHTML = '<ul class="list-group list-group-flush"></ul>';
                const ul = insightsDiv.querySelector('ul');
                d.insights.forEach(insight => {
                    const li = document.createElement('li');
                    li.className = 'list-group-item';
                    li.innerHTML = '<i class="bi bi-info-circle text-primary"></i> ' + insight;
                    ul.appendChild(li);
                });
            } else {
                showAlert(data.error);
            }
        })
        .catch(err => showAlert('Error loading analytics: ' + err));
}

// Load Forecasting Options
function loadForecastingOptions() {
    fetch('/api/sales/products')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const prodSelect = document.getElementById('forecastProduct');
                const regSelect = document.getElementById('forecastRegion');
                prodSelect.innerHTML = '<option value="all">All Products</option>';
                regSelect.innerHTML = '<option value="all">All Regions</option>';
                data.products.slice(1).forEach(p => {
                    const opt = document.createElement('option');
                    opt.value = p; opt.textContent = p;
                    prodSelect.appendChild(opt);
                });
                data.regions.slice(1).forEach(r => {
                    const opt = document.createElement('option');
                    opt.value = r; opt.textContent = r;
                    regSelect.appendChild(opt);
                });
            }
        });
}

// Generate Forecast
document.getElementById('generateForecastBtn').addEventListener('click', function() {
    const btn = this;
    const originalText = showLoading(btn);
    
    const payload = {
        model: document.getElementById('forecastModel').value,
        horizon: document.getElementById('forecastHorizon').value,
        product: document.getElementById('forecastProduct').value,
        region: document.getElementById('forecastRegion').value
    };
    
    fetch('/api/forecast', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify(payload)
    })
    .then(response => response.json())
    .then(data => {
        hideLoading(btn, originalText);
        if (data.success) {
            document.getElementById('forecastResults').style.display = 'block';
            
            // Forecast chart
            if (currentCharts.forecast) currentCharts.forecast.destroy();
            const fCtx = document.getElementById('forecastChart').getContext('2d');
            currentCharts.forecast = new Chart(fCtx, {
                type: 'line',
                data: {
                    labels: data.forecast_results.map(x => x.forecast_date),
                    datasets: [{
                        label: 'Predicted Sales (' + data.model_name + ')',
                        data: data.forecast_results.map(x => x.predicted_sales),
                        borderColor: '#e74c3c',
                        tension: 0.1,
                        fill: false
                    }]
                },
                options: {
                    responsive: true,
                    scales: { y: { beginAtZero: true } }
                }
            });
            
            // Summary
            const sumDiv = document.getElementById('forecastSummary');
            const total = data.forecast_results.reduce((a,b) => a + b.predicted_sales, 0);
            const avg = total / data.forecast_results.length;
            sumDiv.innerHTML = `
                <p><strong>Model:</strong> ${data.model_name}</p>
                <p><strong>Horizon:</strong> ${data.forecast_horizon} days</p>
                <p><strong>Total Predicted:</strong> $${total.toFixed(2)}</p>
                <p><strong>Average Daily:</strong> $${avg.toFixed(2)}</p>
            `;
            
            // Insights
            const finList = document.getElementById('forecastInsightsList');
            finList.innerHTML = '';
            if (data.insights) {
                data.insights.forEach(insight => {
                    const li = document.createElement('li');
                    li.className = 'list-group-item';
                    li.innerHTML = '<i class="bi bi-check-circle text-success"></i> ' + insight;
                    finList.appendChild(li);
                });
            }
            
            // Store for download
            document.getElementById('downloadForecastBtn').dataset.runId = data.run_id;
            showAlert('Forecast generated successfully!', 'success');
        } else {
            showAlert(data.error);
        }
    })
    .catch(err => {
        hideLoading(btn, originalText);
        showAlert('Error generating forecast: ' + err);
    });
});

// Download Forecast
document.getElementById('downloadForecastBtn').addEventListener('click', function() {
    const runId = this.dataset.runId;
    if (runId) {
        window.location.href = '/api/forecast/download?run_id=' + runId;
    } else {
        showAlert('No forecast to download', 'warning');
    }
});

// Compare Models
document.getElementById('compareModelsBtn').addEventListener('click', function() {
    const btn = this;
    const originalText = showLoading(btn);
    
    fetch('/api/compare-models', {
        method: 'POST',
        headers: {'Content-Type': 'application/json'},
        body: JSON.stringify({})
    })
    .then(response => response.json())
    .then(data => {
        hideLoading(btn, originalText);
        if (data.success) {
            const tbody = document.querySelector('#comparisonTable tbody');
            tbody.innerHTML = '';
            Object.entries(data.comparison).forEach(([key, val]) => {
                const tr = document.createElement('tr');
                tr.innerHTML = `
                    <td>${val.model_name || key}</td>
                    <td>${val.mae !== undefined ? val.mae.toFixed(2) : '-'}</td>
                    <td>${val.rmse !== undefined ? val.rmse.toFixed(2) : '-'}</td>
                    <td>${val.mape !== undefined && !isNaN(val.mape) ? val.mape.toFixed(2) + '%' : '-'}</td>
                    <td>${val.wape !== undefined && !isNaN(val.wape) ? val.wape.toFixed(2) + '%' : '-'}</td>
                    <td>${val.r2 !== undefined && !isNaN(val.r2) ? val.r2.toFixed(3) : '-'}</td>
                    <td><span class="badge bg-${val.training_status === 'success' ? 'success' : 'danger'}">${val.training_status}</span></td>
                    <td><span class="badge bg-${val.evaluation_status === 'success' ? 'success' : 'danger'}">${val.evaluation_status}</span></td>
                `;
                tbody.appendChild(tr);
            });
            if (data.best_model) {
                const bestDiv = document.getElementById('bestModelInfo');
                bestDiv.style.display = 'block';
                bestDiv.innerHTML = `<strong>Best Performing Model (based on MAE):</strong> ${data.comparison[data.best_model].model_name}`;
            }
            showAlert('Model comparison completed!', 'success');
        } else {
            showAlert(data.error);
        }
    })
    .catch(err => {
        hideLoading(btn, originalText);
        showAlert('Error comparing models: ' + err);
    });
});

// Upload Form
document.getElementById('uploadForm').addEventListener('submit', function(e) {
    e.preventDefault();
    const fileInput = document.getElementById('csvFile');
    const file = fileInput.files[0];
    if (!file) {
        showAlert('Please select a file', 'warning');
        return;
    }
    
    const formData = new FormData();
    formData.append('file', file);
    
    fetch('/api/upload', {
        method: 'POST',
        body: formData
    })
    .then(response => response.json())
    .then(data => {
        if (data.success) {
            showAlert(data.message, 'success');
            loadDatasetInfo();
        } else {
            showAlert(data.error);
        }
    })
    .catch(err => showAlert('Error uploading file: ' + err));
});

// Load Dataset Info
function loadDatasetInfo() {
    fetch('/api/overview')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const info = document.getElementById('datasetInfo');
                info.innerHTML = `
                    <p><strong>Total Records:</strong> ${data.data.kpis.total_orders}</p>
                    <p><strong>Total Revenue:</strong> $${data.data.kpis.total_revenue.toLocaleString()}</p>
                    <p><strong>Best Selling Product:</strong> ${data.data.kpis.best_selling_product}</p>
                    <p><strong>Date Range:</strong> Available in dataset</p>
                `;
            }
        });
}

// Load History
function loadHistory() {
    fetch('/api/forecast/history')
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                const tbody = document.querySelector('#historyTable tbody');
                tbody.innerHTML = '';
                data.data.forEach(item => {
                    const tr = document.createElement('tr');
                    const date = new Date(item.created_at).toLocaleString();
                    tr.innerHTML = `
                        <td><small>${item.run_id.substring(0,8)}...</small></td>
                        <td>${date}</td>
                        <td>${item.model_name}</td>
                        <td>${item.forecast_horizon} days</td>
                        <td>
                            <a href="/api/forecast/download?run_id=${item.run_id}" class="btn btn-sm btn-success">
                                <i class="bi bi-download"></i> Download
                            </a>
                        </td>
                    `;
                    tbody.appendChild(tr);
                });
            } else {
                showAlert(data.error);
            }
        })
        .catch(err => showAlert('Error loading history: ' + err));
}

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    loadOverview();
});
