// API взаимодействие
const API_BASE = '/api/v1';

class ApiService {
    static async getMenu() {
        try {
            const response = await fetch(`${API_BASE}/menu`);
            if (!response.ok) throw new Error('Network response was not ok');
            return await response.json();
        } catch (error) {
            console.error('Error fetching menu:', error);
            throw error;
        }
    }

    static async createOrder(orderData) {
        try {
            const response = await fetch(`${API_BASE}/orders`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(orderData)
            });
            
            if (!response.ok) {
                const errorData = await response.json();
                throw new Error(errorData.detail || 'Error creating order');
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error creating order:', error);
            throw error;
        }
    }

    static async getOrders(params = {}) {
        try {
            const queryParams = new URLSearchParams(params).toString();
            const response = await fetch(`${API_BASE}/orders?${queryParams}`);
            if (!response.ok) throw new Error('Network response was not ok');
            return await response.json();
        } catch (error) {
            console.error('Error fetching orders:', error);
            throw error;
        }
    }

    static async getCategories() {
        try {
            const response = await fetch(`${API_BASE}/menu/categories`);
            if (!response.ok) throw new Error('Network response was not ok');
            return await response.json();
        } catch (error) {
            console.error('Error fetching categories:', error);
            throw error;
        }
    }

    static async createDish(dishData) {
        try {
            const response = await fetch(`${API_BASE}/menu/dishes`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(dishData)
            });
            
            if (!response.ok) throw new Error('Network response was not ok');
            return await response.json();
        } catch (error) {
            console.error('Error creating dish:', error);
            throw error;
        }
    }
}

export default ApiService;
