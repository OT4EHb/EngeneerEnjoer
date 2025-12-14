// Инициализация Chart.js
let categoryChart = null;

// Загрузка ежедневного отчета
async function loadDailyReport() {
    const date = document.getElementById('daily-date').value;
    if (!date) return;
    
    try {
        const response = await fetch(`/api/reports/daily?report_date=${date}`);
        if (!response.ok) throw new Error('Ошибка загрузки отчета');
        
        const report = await response.json();
        displayDailyReport(report);
        
    } catch (error) {
        console.error('Ошибка:', error);
        document.getElementById('daily-report').innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle"></i> Ошибка: ${error.message}
            </div>
        `;
    }
}

// Отображение ежедневного отчета
function displayDailyReport(report) {
    const container = document.getElementById('daily-report');
    
    let html = `
        <div class="card bg-light">
            <div class="card-body">
                <h6 class="card-title">${report.date}</h6>
                <div class="row text-center">
                    <div class="col">
                        <div class="display-6 text-primary">${report.orders_count}</div>
                        <small class="text-muted">заказов</small>
                    </div>
                    <div class="col">
                        <div class="display-6 text-success">${report.daily_total.toFixed(2)}</div>
                        <small class="text-muted">рублей</small>
                    </div>
                    <div class="col">
                        <div class="display-6 text-info">${report.average_order.toFixed(2)}</div>
                        <small class="text-muted">средний чек</small>
                    </div>
                </div>
            </div>
        </div>
    `;
    
    if (report.orders && report.orders.length > 0) {
        html += `
            <div class="mt-3">
                <h6>Детали заказов:</h6>
                <div class="table-responsive">
                    <table class="table table-sm">
                        <thead>
                            <tr>
                                <th>Время</th>
                                <th>Кол-во позиций</th>
                                <th>Сумма</th>
                            </tr>
                        </thead>
                        <tbody>
        `;
        
        report.orders.forEach(order => {
            html += `
                <tr>
                    <td>${order.time || 'N/A'}</td>
                    <td>${order.item_count}</td>
                    <td class="fw-bold">${order.total.toFixed(2)} ₽</td>
                </tr>
            `;
        });
        
        html += `
                        </tbody>
                    </table>
                </div>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

// Загрузка отчета по категориям
async function loadCategoryReport() {
    const startDate = document.getElementById('cat-start-date').value;
    const endDate = document.getElementById('cat-end-date').value;
    
    if (!startDate || !endDate) return;
    
    try {
        const response = await fetch(`/api/reports/by-category?start_date=${startDate}&end_date=${endDate}`);
        if (!response.ok) throw new Error('Ошибка загрузки отчета');
        
        const report = await response.json();
        displayCategoryChart(report);
        
    } catch (error) {
        console.error('Ошибка:', error);
        alert(`Ошибка: ${error.message}`);
    }
}

// Отображение графика по категориям
function displayCategoryChart(report) {
    const ctx = document.getElementById('categoryChart').getContext('2d');
    
    // Если есть предыдущий график, удаляем его
    if (categoryChart) {
        categoryChart.destroy();
    }
    
    const labels = report.categories.map(item => item.category);
    const data = report.categories.map(item => item.amount);
    const colors = generateColors(labels.length);
    
    categoryChart = new Chart(ctx, {
        type: 'pie',
        data: {
            labels: labels,
            datasets: [{
                data: data,
                backgroundColor: colors,
                borderColor: 'white',
                borderWidth: 2
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: {
                    position: 'right',
                    labels: {
                        boxWidth: 12,
                        padding: 15
                    }
                },
                tooltip: {
                    callbacks: {
                        label: function(context) {
                            const item = report.categories[context.dataIndex];
                            return `${item.category}: ${item.amount.toFixed(2)} ₽ (${item.percentage}%)`;
                        }
                    }
                }
            }
        }
    });
}

// Загрузка популярных блюд
async function loadPopularDishes() {
    const limit = document.getElementById('popular-limit').value;
    
    try {
        const response = await fetch(`/api/reports/popular-dishes?limit=${limit}`);
        if (!response.ok) throw new Error('Ошибка загрузки данных');
        
        const dishes = await response.json();
        displayPopularDishes(dishes);
        
    } catch (error) {
        console.error('Ошибка:', error);
        document.getElementById('popular-dishes').innerHTML = `
            <tr>
                <td colspan="4" class="text-center text-danger">
                    <i class="bi bi-exclamation-triangle"></i> Ошибка: ${error.message}
                </td>
            </tr>
        `;
    }
}

// Отображение популярных блюд
function displayPopularDishes(dishes) {
    const tableBody = document.getElementById('popular-dishes');
    
    if (!dishes || dishes.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="4" class="text-center text-muted">
                    <i class="bi bi-info-circle"></i> Нет данных
                </td>
            </tr>
        `;
        return;
    }
    
    let html = '';
    
    dishes.forEach((dish, index) => {
        const medal = index === 0 ? '🥇' : index === 1 ? '🥈' : index === 2 ? '🥉' : `${index + 1}.`;
        
        html += `
            <tr>
                <td>
                    <span class="me-2">${medal}</span>
                    ${dish.dish}
                </td>
                <td>${dish.category}</td>
                <td class="fw-bold">${dish.sold}</td>
                <td class="text-success fw-bold">${dish.revenue.toFixed(2)} ₽</td>
            </tr>
        `;
    });
    
    tableBody.innerHTML = html;
}

// Генерация цветов для графика
function generateColors(count) {
    const colors = [
        '#FF6384', '#36A2EB', '#FFCE56', '#4BC0C0', 
        '#9966FF', '#FF9F40', '#8AC926', '#1982C4',
        '#6A4C93', '#F25F5C', '#FFB347', '#7AE582'
    ];
    
    // Если нужно больше цветов, генерируем случайные
    if (count <= colors.length) {
        return colors.slice(0, count);
    }
    
    const result = [...colors];
    for (let i = colors.length; i < count; i++) {
        result.push(`#${Math.floor(Math.random() * 16777215).toString(16).padStart(6, '0')}`);
    }
    
    return result;
}

// Автоматическая загрузка популярных блюд при открытии страницы
document.addEventListener('DOMContentLoaded', function() {
    loadPopularDishes();
    loadCategoryReport();
    loadDailyReport();
});
