// Работа с меню
import ApiService from './api.js';

class MenuManager {
    constructor() {
        this.categories = [];
        this.dishes = [];
        this.dishesByCategory = {};
        this.currentCategory = 'all';
    }

    async loadMenu() {
        try {
            const data = await ApiService.getMenu();
            this.categories = data.categories || [];
            this.dishes = data.dishes || [];
            
            // Группируем блюда по категориям
            this.dishesByCategory = {};
            this.dishesByCategory['all'] = this.dishes.filter(d => d.is_available);
            
            this.categories.forEach(category => {
                this.dishesByCategory[category.id] = this.dishes.filter(
                    dish => dish.category_id === category.id && dish.is_available
                );
            });
            
            return true;
        } catch (error) {
            console.error('Error loading menu:', error);
            throw error;
        }
    }

    getCategoryName(categoryId) {
        const category = this.categories.find(c => c.id === categoryId);
        return category ? category.name : 'Без категории';
    }

    getDish(dishId) {
        return this.dishes.find(d => d.id === dishId);
    }

    getDishesByCategory(categoryId) {
        return this.dishesByCategory[categoryId] || [];
    }

    renderCategories(onCategoryChange) {
        let html = `
            <div class="category-tab ${this.currentCategory === 'all' ? 'active' : ''}" 
                 onclick="app.menu.changeCategory('all', app)">
                <i class="fas fa-th-large"></i> Все
            </div>
        `;
        
        this.categories.forEach(category => {
            const dishCount = this.dishesByCategory[category.id]?.length || 0;
            if (dishCount > 0) {
                html += `
                    <div class="category-tab ${this.currentCategory === category.id ? 'active' : ''}" 
                         onclick="app.menu.changeCategory('${category.id}', app)">
                        ${category.name} (${dishCount})
                    </div>
                `;
            }
        });
        
        return html;
    }

    renderDishes(onAddToOrder) {
        const dishes = this.dishesByCategory[this.currentCategory] || [];
        
        if (dishes.length === 0) {
            return '<p style="grid-column: 1 / -1; text-align: center; padding: 40px; color: #7f8c8d;">Нет доступных блюд</p>';
        }
        
        let html = '';
        
        dishes.forEach(dish => {
            html += `
                <div class="dish-card" onclick="app.order.addToOrder('${dish.id}')">
                    <h3>${dish.name}</h3>
                    <div class="dish-price">${dish.price.toFixed(2)} ₽</div>
                    <button class="add-quick" onclick="event.stopPropagation(); app.order.addToOrder('${dish.id}')">
                        <i class="fas fa-plus"></i> Добавить
                    </button>
                </div>
            `;
        });
        
        return html;
    }

    changeCategory(categoryId, app) {
        this.currentCategory = categoryId;
        if (app && app.render) {
            app.render();
        }
    }
}

export default MenuManager;
