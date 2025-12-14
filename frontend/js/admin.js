// Глобальные переменные
let categories = [];
let dishes = [];

// Инициализация
document.addEventListener('DOMContentLoaded', function() {
    loadCategories();
    loadDishes();
});

// ========== КАТЕГОРИИ ==========

// Загрузка категорий
async function loadCategories() {
    try {
        const response = await fetch('/api/admin/categories');
        if (!response.ok) throw new Error('Ошибка загрузки категорий');
        
        categories = await response.json();
        displayCategories();
        
    } catch (error) {
        console.error('Ошибка:', error);
        document.getElementById('categories-table').innerHTML = `
            <tr>
                <td colspan="3" class="text-center text-danger">
                    <i class="bi bi-exclamation-triangle"></i> Ошибка загрузки: ${error.message}
                </td>
            </tr>
        `;
    }
}

// Отображение категорий
function displayCategories() {
    const tableBody = document.getElementById('categories-table');
    
    if (categories.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="3" class="text-center text-muted">
                    <i class="bi bi-info-circle"></i> Категории не добавлены
                </td>
            </tr>
        `;
        return;
    }
    
    let html = '';
    
    categories.forEach(category => {
        html += `
            <tr>
                <td><small class="text-muted">${category.category_id.substring(0, 8)}...</small></td>
                <td>${category.name}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="editCategory('${category.category_id}', '${category.name}')">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteCategory('${category.category_id}', '${category.name}')">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    tableBody.innerHTML = html;
}

// Показать модальное окно категории
function showCategoryModal(categoryId = null, categoryName = '') {
    document.getElementById('categoryId').value = categoryId || '';
    document.getElementById('categoryName').value = categoryName;
    
    const modal = new bootstrap.Modal(document.getElementById('categoryModal'));
    const modalTitle = document.querySelector('#categoryModal .modal-title');
    
    modalTitle.textContent = categoryId ? 'Редактировать категорию' : 'Добавить категорию';
    modal.show();
}

// Сохранить категорию
async function saveCategory() {
    const categoryId = document.getElementById('categoryId').value;
    const categoryName = document.getElementById('categoryName').value.trim();
    
    if (!categoryName) {
        alert('Введите название категории');
        return;
    }
    
    const url = categoryId 
        ? `/api/admin/categories/${categoryId}`
        : '/api/admin/categories';
    
    const method = categoryId ? 'PUT' : 'POST';
    
    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ name: categoryName })
        });
        
        if (!response.ok) throw new Error('Ошибка сохранения');
        
        const modal = bootstrap.Modal.getInstance(document.getElementById('categoryModal'));
        modal.hide();
        
        loadCategories(); // Перезагружаем список
        showNotification('Категория сохранена!', 'success');
        
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification(`Ошибка: ${error.message}`, 'danger');
    }
}

// Редактировать категорию
function editCategory(categoryId, categoryName) {
    showCategoryModal(categoryId, categoryName);
}

// Удалить категорию
async function deleteCategory(categoryId, categoryName) {
    if (!confirm(`Удалить категорию "${categoryName}"?`)) return;
    
    try {
        const response = await fetch(`/api/admin/categories/${categoryId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Ошибка удаления');
        }
        
        loadCategories(); // Перезагружаем список
        loadDishes(); // Перезагружаем блюда (могли измениться категории)
        showNotification('Категория удалена!', 'success');
        
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification(`Ошибка: ${error.message}`, 'danger');
    }
}

// ========== БЛЮДА ==========

// Загрузка блюд
async function loadDishes() {
    try {
        const response = await fetch('/api/admin/dishes');
        if (!response.ok) throw new Error('Ошибка загрузки блюд');
        
        dishes = await response.json();
        displayDishes();
        
        // Обновляем список категорий в модальном окне
        updateCategorySelect();
        
    } catch (error) {
        console.error('Ошибка:', error);
        document.getElementById('dishes-table').innerHTML = `
            <tr>
                <td colspan="4" class="text-center text-danger">
                    <i class="bi bi-exclamation-triangle"></i> Ошибка загрузки: ${error.message}
                </td>
            </tr>
        `;
    }
}

// Отображение блюд
function displayDishes() {
    const tableBody = document.getElementById('dishes-table');
    
    if (dishes.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="4" class="text-center text-muted">
                    <i class="bi bi-info-circle"></i> Блюда не добавлены
                </td>
            </tr>
        `;
        return;
    }
    
    let html = '';
    
    dishes.forEach(dish => {
        html += `
            <tr>
                <td>${dish.name}</td>
                <td>${dish.price} ₽</td>
                <td>${dish.category_name || 'Без категории'}</td>
                <td>
                    <button class="btn btn-sm btn-outline-primary me-1" onclick="editDish('${dish.dish_id}', '${dish.name}', ${dish.price}, '${dish.category_id}')">
                        <i class="bi bi-pencil"></i>
                    </button>
                    <button class="btn btn-sm btn-outline-danger" onclick="deleteDish('${dish.dish_id}', '${dish.name}')">
                        <i class="bi bi-trash"></i>
                    </button>
                </td>
            </tr>
        `;
    });
    
    tableBody.innerHTML = html;
}

// Обновление select с категориями
function updateCategorySelect() {
    const select = document.getElementById('dishCategory');
    select.innerHTML = '<option value="">Выберите категорию</option>';
    
    categories.forEach(category => {
        select.innerHTML += `<option value="${category.category_id}">${category.name}</option>`;
    });
}

// Показать модальное окно блюда
function showDishModal(dishId = null, dishName = '', dishPrice = 0, categoryId = '') {
    document.getElementById('dishId').value = dishId || '';
    document.getElementById('dishName').value = dishName;
    document.getElementById('dishPrice').value = dishPrice;
    document.getElementById('dishCategory').value = categoryId;
    
    const modal = new bootstrap.Modal(document.getElementById('dishModal'));
    const modalTitle = document.querySelector('#dishModal .modal-title');
    
    modalTitle.textContent = dishId ? 'Редактировать блюдо' : 'Добавить блюдо';
    modal.show();
}

// Сохранить блюдо
async function saveDish() {
    const dishId = document.getElementById('dishId').value;
    const dishName = document.getElementById('dishName').value.trim();
    const dishPrice = parseFloat(document.getElementById('dishPrice').value);
    const categoryId = document.getElementById('dishCategory').value;
    
    if (!dishName || !dishPrice || !categoryId) {
        alert('Заполните все поля');
        return;
    }
    
    const dishData = {
        name: dishName,
        price: dishPrice,
        category_id: categoryId
    };
    
    const url = dishId 
        ? `/api/admin/dishes/${dishId}`
        : '/api/admin/dishes';
    
    const method = dishId ? 'PUT' : 'POST';
    
    try {
        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(dishData)
        });
        
        if (!response.ok) throw new Error('Ошибка сохранения');
        
        const modal = bootstrap.Modal.getInstance(document.getElementById('dishModal'));
        modal.hide();
        
        loadDishes(); // Перезагружаем список
        showNotification('Блюдо сохранено!', 'success');
        
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification(`Ошибка: ${error.message}`, 'danger');
    }
}

// Редактировать блюдо
function editDish(dishId, dishName, dishPrice, categoryId) {
    showDishModal(dishId, dishName, dishPrice, categoryId);
}

// Удалить блюдо
async function deleteDish(dishId, dishName) {
    if (!confirm(`Удалить блюдо "${dishName}"?`)) return;
    
    try {
        const response = await fetch(`/api/admin/dishes/${dishId}`, {
            method: 'DELETE'
        });
        
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Ошибка удаления');
        }
        
        loadDishes(); // Перезагружаем список
        showNotification('Блюдо удалено!', 'success');
        
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification(`Ошибка: ${error.message}`, 'danger');
    }
}

// ========== ЗАКАЗЫ ==========

// Загрузка заказов
/*async function loadOrders() {
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;
    
    if (!startDate || !endDate) {
        alert('Выберите даты');
        return;
    }
    
    try {
        const response = await fetch(`/api/reports/daily?report_date=${startDate}`);
        if (!response.ok) throw new Error('Ошибка загрузки заказов');
        
        const data = await response.json();
        displayOrders(data.orders);
        
    } catch (error) {
        console.error('Ошибка:', error);
        document.getElementById('orders-table').innerHTML = `
            <tr>
                <td colspan="4" class="text-center text-danger">
                    <i class="bi bi-exclamation-triangle"></i> Ошибка загрузки: ${error.message}
                </td>
            </tr>
        `;
    }
}*/

// Загрузка заказов
async function loadOrders() {
    const startDate = document.getElementById('start-date').value;
    const endDate = document.getElementById('end-date').value;
    
    try {
        // Строим URL с параметрами
        let url = '/api/admin/orders/by-date';
        const params = new URLSearchParams();
        
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);
        
        if (params.toString()) {
            url += '?' + params.toString();
        }
        
        const response = await fetch(url);
        if (!response.ok) {
            const errorData = await response.json();
            throw new Error(errorData.detail || 'Ошибка загрузки заказов');
        }
        
        const orders = await response.json();
        displayOrders(orders);
        
    } catch (error) {
        console.error('Ошибка:', error);
        document.getElementById('orders-table').innerHTML = `
            <tr>
                <td colspan="4" class="text-center text-danger">
                    <i class="bi bi-exclamation-triangle"></i> ${error.message}
                </td>
            </tr>
        `;
    }
}

// Отображение заказов
/*function displayOrders(orders) {
    const tableBody = document.getElementById('orders-table');
    
    if (!orders || orders.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="4" class="text-center text-muted">
                    <i class="bi bi-info-circle"></i> Заказов за выбранный период нет
                </td>
            </tr>
        `;
        return;
    }
    
    let html = '';
    
    orders.forEach(order => {
        const date = new Date(order.time || order.order_date);
        const time = date.toLocaleTimeString([], {hour: '2-digit', minute:'2-digit'});
        
        html += `
            <tr>
                <td>
                    <small class="text-muted">${time}</small>
                </td>
                <td><small class="text-muted">${order.order_id?.substring(0, 8) || 'N/A'}...</small></td>
                <td class="fw-bold text-success">${order.total || order.total_amount} ₽</td>
                <td>
                    <button class="btn btn-sm btn-outline-info" onclick="viewOrderDetails('${order.order_id}')">
                        <i class="bi bi-eye"></i> Детали
                    </button>
                </td>
            </tr>
        `;
    });
    
    tableBody.innerHTML = html;
}*/

// Отображение заказов
function displayOrders(orders) {
    const tableBody = document.getElementById('orders-table');
    
    if (!orders || orders.length === 0) {
        tableBody.innerHTML = `
            <tr>
                <td colspan="4" class="text-center text-muted">
                    <i class="bi bi-info-circle"></i> Заказов за выбранный период нет
                </td>
            </tr>
        `;
        return;
    }
    
    let html = '';
    
    orders.forEach(order => {
        // Правильный парсинг даты
        let displayDate = 'Нет даты';
        let displayTime = '';
        
        if (order.order_date) {
            const dateObj = new Date(order.order_date);
             
            if (!isNaN(dateObj.getTime())) {
                // Форматируем дату: ДД.ММ.ГГГГ ЧЧ:ММ
                const day = dateObj.getDate().toString().padStart(2, '0');
                const month = (dateObj.getMonth() + 1).toString().padStart(2, '0');
                const year = dateObj.getFullYear();
                const hours = dateObj.getHours().toString().padStart(2, '0');
                const minutes = dateObj.getMinutes().toString().padStart(2, '0');
                
                displayDate = `${day}.${month}.${year}`;
                displayTime = `${hours}:${minutes}`;
            }
        }
        
        html += `
            <tr>
                <td>
                    <div class="small text-muted">${displayDate}</div>
                    <div class="small">${displayTime}</div>
                </td>
                <td><small class="text-muted">${order.order_id?.substring(0, 8) || 'N/A'}...</small></td>
                <td class="fw-bold text-success">${order.total_amount || order.total} ₽</td>
                <td>
                    <button class="btn btn-sm btn-outline-info" onclick="viewOrderDetails('${order.order_id}')">
                        <i class="bi bi-eye"></i> Детали
                    </button>
                </td>
            </tr>
        `;
    });
    
    tableBody.innerHTML = html;
}

// Просмотр деталей заказа
async function viewOrderDetails(orderId) {
    try {
        const response = await fetch(`/api/cashier/orders/${orderId}`);
        if (!response.ok) throw new Error('Ошибка загрузки деталей');
        
        const order = await response.json();
        
        let itemsHtml = '';
        order.items.forEach(item => {
            itemsHtml += `
                <tr>
                    <td>${item.dish_name}</td>
                    <td class="text-end">${item.quantity}</td>
                    <td class="text-end">${item.price_per_item} ₽</td>
                    <td class="text-end fw-bold">${item.item_total} ₽</td>
                </tr>
            `;
        });
        
        const modalHtml = `
            <div class="modal fade" id="orderDetailsModal" tabindex="-1">
                <div class="modal-dialog modal-lg">
                    <div class="modal-content">
                        <div class="modal-header">
                            <h5 class="modal-title">Заказ #${order.order_id.substring(0, 8)}</h5>
                            <button type="button" class="btn-close" data-bs-dismiss="modal"></button>
                        </div>
                        <div class="modal-body">
                            <div class="row mb-3">
                                <div class="col">
                                    <strong>Дата:</strong> ${new Date(order.order_date).toLocaleString()}
                                </div>
                                <div class="col text-end">
                                    <strong>Итого:</strong> <span class="text-success fw-bold">${order.total_amount} ₽</span>
                                </div>
                            </div>
                            
                            <div class="table-responsive">
                                <table class="table table-sm">
                                    <thead>
                                        <tr>
                                            <th>Блюдо</th>
                                            <th class="text-end">Кол-во</th>
                                            <th class="text-end">Цена</th>
                                            <th class="text-end">Сумма</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${itemsHtml}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                        <div class="modal-footer">
                            <button type="button" class="btn btn-secondary" data-bs-dismiss="modal">Закрыть</button>
                        </div>
                    </div>
                </div>
            </div>
        `;
        
        // Удаляем предыдущее модальное окно если есть
        const existingModal = document.getElementById('orderDetailsModal');
        if (existingModal) existingModal.remove();
        
        // Добавляем новое модальное окно
        document.body.insertAdjacentHTML('beforeend', modalHtml);
        
        // Показываем модальное окно
        const modal = new bootstrap.Modal(document.getElementById('orderDetailsModal'));
        modal.show();
        
    } catch (error) {
        console.error('Ошибка:', error);
        showNotification(`Ошибка: ${error.message}`, 'danger');
    }
}

// ========== ОБЩИЕ ФУНКЦИИ ==========

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

// Инициализация дат
function initDates() {
    const today = new Date().toISOString().split('T')[0];
    document.getElementById('start-date').value = today;
    document.getElementById('end-date').value = today;
}

// Инициализируем даты при загрузке
initDates();
