// Основной файл приложения
import CashierApp from './cashier.js';

// Создаем глобальный объект приложения
const app = new CashierApp();

// Инициализация при загрузке страницы
document.addEventListener('DOMContentLoaded', async () => {
    try {
        await app.init();
        
        // Делаем app доступным глобально для обработчиков onclick
        window.app = app;
        
        console.log('Application started successfully');
    } catch (error) {
        console.error('Failed to start application:', error);
        
        // Показываем ошибку пользователю
        document.getElementById('app').innerHTML = `
            <div class="container" style="text-align: center; padding: 50px; color: white;">
                <h1><i class="fas fa-exclamation-triangle"></i> Ошибка загрузки</h1>
                <p>Не удалось загрузить приложение. Пожалуйста, обновите страницу.</p>
                <button onclick="location.reload()" style="padding: 10px 20px; margin-top: 20px; background: #3498db; color: white; border: none; border-radius: 5px; cursor: pointer;">
                    <i class="fas fa-redo"></i> Обновить страницу
                </button>
            </div>
        `;
    }
});

// Экспортируем для использования в других модулях
export default app;
