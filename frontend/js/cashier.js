// Глобальные переменные
let currentOrder = [];
let menuData = {};

// Загрузка страницы
document.addEventListener('DOMContentLoaded', function() {
    loadMenu();
    loadTodayOrders();
    
    // Обновляем кнопку каждые 30 секунд
    setInterval(loadTodayOrders, 30000);
});

// Загрузка меню
async function loadMenu() {
    try {
        const response = await fetch('/api/cashier/menu');
        if (!response.ok) throw new Error('Ошибка загрузки меню');
        
        menuData = await response.json();
        displayMenu();
        
    } catch (error) {
        console.error('Ошибка:', error);
        document.getElementById('menu').innerHTML = `
            <div class="alert alert-danger">
                <i class="bi bi-exclamation-triangle"></i> Ошибка загрузки меню: ${error.message}
            </div>
        `;
    }
}

// Отображение меню
function displayMenu() {
    const menuContainer = document.getElementById('menu');
    
    if (Object.keys(menuData).length === 0) {
        menuContainer.innerHTML = `
            <div class="alert alert-warning">
                <i class="bi bi-info-circle"></i> Меню пустое. Добавьте блюда через панель администратора.
            </div>
        `;
        return;
    }
    
    let html = '';
    
    for (const [category, dishes] of Object.entries(menuData)) {
        html += `
            <div class="category-card mb-4 p-3 rounded">
                <h6 class="mb-3">
                    <i class="bi bi-tag"></i> ${category}
                </h6>
                <div class="row row-cols-1 row-cols-md-2 g-3">
        `;
        
        dishes.forEach(dish => {
            html += `
                <div class="col">
                    <div class="dish-card card h-100" onclick="addToOrder('${dish.dish_id}', '${dish.name}', ${dish.price})">
                        <div class="card-body">
                            <div class="d-flex justify-content-between align-items-start">
                                <div>
                                    <h6 class="card-title mb-1">${dish.name}</h6>
                                    <p class="card-text text-success fw-bold mb-0">
                                        ${dish.price.toFixed(2)} ₽
                                    </p>
                                </div>
                                <button class="btn btn-sm btn-outline-primary">
                                    <i class="bi bi-plus"></i> Добавить
                                </button>
                            </div>
                        </div>
                    </div>
                </div>
            `;
        });
        
        html += `
                </div>
            </div>
        `;
    }
    
    menuContainer.innerHTML = html;
}

// Добавление блюда в заказ
function addToOrder(dishId, name, price) {
    // Проверяем, есть ли уже это блюдо в заказе
    const existingItem = currentOrder.find(item => item.dishId === dishId);
    
    if (existingItem) {
        existingItem.quantity += 1;
        existingItem.total = existingItem.quantity * price;
    } else {
        currentOrder.push({
            dishId: dishId,
            name: name,
            price: price,
            quantity: 1,
            total: price
        });
    }
    
    updateOrderDisplay();
    updateSubmitButton();
}

// Обновление отображения заказа
function updateOrderDisplay() {
    const orderContainer = document.getElementById('order-items');
    const totalAmountElement = document.getElementById('total-amount');
    
    if (currentOrder.length === 0) {
        orderContainer.innerHTML = '<p class="text-muted text-center">Заказ пуст. Выберите блюда из меню.</p>';
        totalAmountElement.textContent = '0.00 ₽';
        return;
    }
    
    let total = 0;
    let html = '';
    
    currentOrder.forEach((item, index) => {
        total += item.total;
        
        html += `
            <div class="order-item d-flex justify-content-between align-items-center">
                <div class="flex-grow-1">
                    <div class="fw-medium">${item.name}</div>
                    <small class="text-muted">${item.price.toFixed(2)} ₽ × ${item.quantity}</small>
                </div>
                <div class="d-flex align-items-center">
                    <span class="badge bg-primary rounded-pill quantity-badge me-2" 
                          onclick="changeQuantity(${index}, -1)">-</span>
                    <span class="fw-bold me-2">${item.quantity}</span>
                    <span class="badge bg-primary rounded-pill quantity-badge me-3" 
                          onclick="changeQuantity(${index}, 1)">+</span>
                    <span class="fw-bold text-success">${item.total.toFixed(2)} ₽</span>
                    <button class="btn btn-sm btn-outline-danger ms-2" 
                            onclick="removeFromOrder(${index})">
                        <i class="bi bi-trash"></i>
                    </button>
                </div>
            </div>
        `;
    });
    
    orderContainer.innerHTML = html;
    totalAmountElement.textContent = `${total.toFixed(2)} ₽`;
}

// Изменение количества
function changeQuantity(index, delta) {
    const item = currentOrder[index];
    const newQuantity = item.quantity + delta;
    
    if (newQuantity < 1) {
        removeFromOrder(index);
        return;
    }
    
    item.quantity = newQuantity;
    item.total = item.price * newQuantity;
    
    updateOrderDisplay();
    updateSubmitButton();
}

// Удаление из заказа
function removeFromOrder(index) {
    currentOrder.splice(index, 1);
    updateOrderDisplay();
    updateSubmitButton();
}

// Обновление состояния кнопки оформления
function updateSubmitButton() {
    const submitButton = document.getElementById('submit-order');
    submitButton.disabled = currentOrder.length === 0;
}

// Очистка заказа
function clearOrder() {
    if (currentOrder.length === 0) return;
    
    if (confirm('Очистить текущий заказ?')) {
        currentOrder = [];
        updateOrderDisplay();
        updateSubmitButton();
    }
}

// Оформление заказа
async function submitOrder() {
    if (currentOrder.length === 0) return;
    
    const orderData = {
        items: currentOrder.map(item => ({
            dish_id: item.dishId,
            quantity: item.quantity
        }))
    };
    
    const submitButton = document.getElementById('submit-order');
    const originalText = submitButton.innerHTML;
    
    // Показываем индикатор загрузки
    submitButton.disabled = true;
    submitButton.innerHTML = `
        <span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span>
        Оформление...
    `;
    
    try {
        const response = await fetch('/api/cashier/order', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(orderData)
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Ошибка сервера');
        }
        
        const result = await response.json();
        
        // Показываем уведомление об успехе
        showNotification(`Заказ #${result.order_id.substring(0, 8)} оформлен! Сумма: ${result.total_amount.toFixed(2)} ₽`, 'success');
        
        // Сбрасываем заказ
        currentOrder = [];
        updateOrderDisplay();
        updateSubmitButton();
        
        // Обновляем список сегодняшних заказов
        loadTodayOrders();
        
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification(`Ошибка: ${error.message}`, 'danger');
    } finally {
        // Восстанавливаем кнопку
        submitButton.disabled = false;
        submitButton.innerHTML = originalText;
    }
}

// Показать уведомление
function showNotification(message, type = 'info') {
    const alert = document.createElement('div');
    alert.className = `alert alert-${type} alert-dismissible fade show position-fixed`;
    alert.style.cssText = `
        top: 20px;
        right: 20px;
        z-index: 1050;
        min-width: 300px;
        max-width: 400px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.15);
    `;
    
    alert.innerHTML = `
        ${message}
        <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
    `;
    
    document.body.appendChild(alert);
    
    // Автоматическое скрытие через 5 секунд
    setTimeout(() => {
        if (alert.parentNode) {
            alert.remove();
        }
    }, 5000);
}

// Загрузка сегодняшних заказов
async function loadTodayOrders() {
    try {
        const response = await fetch('/api/cashier/orders/today');
        if (!response.ok) return;
        
        const orders = await response.json();
        displayTodayOrders(orders);
        
    } catch (error) {
        console.error('Ошибка загрузки заказов:', error);
    }
}

// Отображение сегодняшних заказов
function displayTodayOrders(orders) {
    const container = document.getElementById('today-orders');
    
    if (!orders || orders.length === 0) {
        container.innerHTML = `
            <p class="text-muted text-center">
                <i class="bi bi-inbox"></i> Сегодня еще не было заказов
            </p>
        `;
        return;
    }
    
    let html = '';
    
    orders.slice(0, 5).forEach(order => {
        const time = new Date(order.order_date).toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        html += `
            <div class="d-flex justify-content-between align-items-center mb-2">
                <div>
                    <small class="text-muted">${time}</small>
                    <div class="small">${order.item_count} ${pluralize(order.item_count, ['позиция', 'позиции', 'позиций'])}</div>
                </div>
                <div class="fw-bold text-success">
                    ${parseFloat(order.total_amount).toFixed(2)} ₽
                </div>
            </div>
        `;
    });
    
    if (orders.length > 5) {
        html += `
            <div class="text-center mt-2">
                <small class="text-muted">
                    и еще ${orders.length - 5} ${pluralize(orders.length - 5, ['заказ', 'заказа', 'заказов'])}
                </small>
            </div>
        `;
    }
    
    container.innerHTML = html;
}

// Функция для правильного склонения
function pluralize(number, words) {
    const cases = [2, 0, 1, 1, 1, 2];
    return words[(number % 100 > 4 && number % 100 < 20) ? 2 : cases[Math.min(number % 10, 5)]];
}
