// Работа с заказами
import ApiService from './api.js';

class OrderManager {
    constructor(menuManager) {
        this.menu = menuManager;
        this.items = [];
        this.cashPaid = 0;
    }

    addToOrder(dishId) {
        const dish = this.menu.getDish(dishId);
        if (!dish) {
            console.error('Dish not found:', dishId);
            return;
        }

        const existingItem = this.items.find(item => item.dish_id === dishId);
        
        if (existingItem) {
            existingItem.quantity += 1;
            existingItem.item_total = existingItem.quantity * dish.price;
        } else {
            this.items.push({
                dish_id: dishId,
                name: dish.name,
                price: dish.price,
                quantity: 1,
                item_total: dish.price
            });
        }
        
        // Анимация добавления
        this.animateDishCard(dishId);
    }

    addCustomItem(name, price, quantity = 1) {
        if (!name || !price || price <= 0 || quantity < 1) {
            throw new Error('Invalid item data');
        }

        const customId = 'custom_' + Date.now();
        
        const existingItem = this.items.find(item => item.name === name);
        
        if (existingItem) {
            existingItem.quantity += quantity;
            existingItem.item_total = existingItem.quantity * price;
        } else {
            this.items.push({
                dish_id: customId,
                name: name,
                price: price,
                quantity: quantity,
                item_total: price * quantity
            });
        }
    }

    updateItemQuantity(dishId, newQuantity) {
        const item = this.items.find(item => item.dish_id === dishId);
        if (!item) return;
        
        if (newQuantity < 1) {
            this.removeItem(dishId);
            return;
        }
        
        item.quantity = newQuantity;
        item.item_total = item.quantity * item.price;
    }

    removeItem(dishId) {
        this.items = this.items.filter(item => item.dish_id !== dishId);
    }

    clearOrder() {
        this.items = [];
        this.cashPaid = 0;
    }

    getTotalAmount() {
        return this.items.reduce((sum, item) => sum + item.item_total, 0);
    }

    getTotalQuantity() {
        return this.items.reduce((sum, item) => sum + item.quantity, 0);
    }

    getChangeAmount() {
        return Math.max(0, this.cashPaid - this.getTotalAmount());
    }

    async saveOrder(customerName = 'Касса', customerPhone = null) {
        if (this.items.length === 0) {
            throw new Error('No items in order');
        }

        const orderData = {
            customer_name: customerName,
            customer_phone: customerPhone,
            items: this.items.map(item => ({
                dish_id: item.dish_id,
                quantity: item.quantity,
                item_total: item.item_total
            }))
        };

        try {
            const order = await ApiService.createOrder(orderData);
            return order;
        } catch (error) {
            console.error('Error saving order:', error);
            throw error;
        }
    }

    renderOrderItems() {
        if (this.items.length === 0) {
            return `
                <div class="empty-order" id="empty-order">
                    <i class="fas fa-shopping-basket"></i>
                    <h3>Нет товаров</h3>
                    <p>Добавьте блюда из меню</p>
                </div>
            `;
        }

        let html = '';
        
        this.items.forEach(item => {
            html += `
                <div class="order-item">
                    <div class="order-item-info">
                        <div class="order-item-name">${item.name}</div>
                        <div class="order-item-price">${item.price.toFixed(2)} ₽ × ${item.quantity}</div>
                    </div>
                    <div class="order-item-actions">
                        <div class="quantity-control">
                            <button class="quantity-btn" onclick="app.order.updateItemQuantity('${item.dish_id}', ${item.quantity - 1})">
                                <i class="fas fa-minus"></i>
                            </button>
                            <span class="quantity">${item.quantity}</span>
                            <button class="quantity-btn" onclick="app.order.updateItemQuantity('${item.dish_id}', ${item.quantity + 1})">
                                <i class="fas fa-plus"></i>
                            </button>
                        </div>
                        <button class="remove-btn" onclick="app.order.removeItem('${item.dish_id}')">
                            <i class="fas fa-trash"></i>
                        </button>
                    </div>
                </div>
            `;
        });
        
        return html;
    }

    renderOrderSummary() {
        const totalAmount = this.getTotalAmount();
        const totalQuantity = this.getTotalQuantity();
        const change = this.getChangeAmount();

        return `
            <div class="summary-line">
                <span>Количество позиций:</span>
                <span>${this.items.length}</span>
            </div>
            <div class="summary-line">
                <span>Итого товаров:</span>
                <span>${totalQuantity}</span>
            </div>
            <div class="summary-line total">
                <span>К ОПЛАТЕ:</span>
                <span>${totalAmount.toFixed(2)} ₽</span>
            </div>
            <div class="summary-line">
                <span>Наличные:</span>
                <input type="number" id="cash-paid" placeholder="0.00" 
                       value="${this.cashPaid > 0 ? this.cashPaid.toFixed(2) : ''}"
                       style="width: 120px; padding: 5px; text-align: right; border: 1px solid #ddd; border-radius: 4px;">
                <span>₽</span>
            </div>
            <div class="summary-line">
                <span>Сдача:</span>
                <span id="change-amount" style="color: ${change >= 0 ? '#27ae60' : '#e74c3c'}">
                    ${change.toFixed(2)} ₽
                </span>
            </div>
        `;
    }

    setCashPaid(amount) {
        this.cashPaid = parseFloat(amount) || 0;
    }

    animateDishCard(dishId) {
        const dishCard = document.querySelector(`.dish-card[onclick*="${dishId}"]`);
        if (dishCard) {
            dishCard.classList.add('selected');
            setTimeout(() => dishCard.classList.remove('selected'), 300);
        }
    }
}

export default OrderManager;
