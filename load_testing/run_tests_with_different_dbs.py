# load_testing/run_tests_with_different_dbs.py
import subprocess
import time
import os
import shutil
from datetime import datetime
import matplotlib.pyplot as plt
import pandas as pd

class DatabaseSwitcher:
    """Класс для переключения между тестовыми БД"""
    
    def __init__(self, app_db_path="instance/canteen.db"):
        self.app_db_path = app_db_path
        self.backup_path = app_db_path+".backup"
        
        # Создаем папку для результатов
        os.makedirs("load_testing/results", exist_ok=True)
    
    def backup_current_db(self):
        """Создание резервной копии текущей БД"""
        if os.path.exists(self.app_db_path):
            shutil.copy2(self.app_db_path, self.backup_path)
            print(f"✓ Создана резервная копия: {self.backup_path}")
            return True
        return False
    
    def restore_backup(self):
        """Восстановление БД из резервной копии"""
        if os.path.exists(self.backup_path):
            shutil.copy2(self.backup_path, self.app_db_path)
            print(f"✓ Восстановлена БД из резервной копии")
            return True
        return False
    
    def switch_to_test_db(self, size):
        """Переключение на тестовую БД указанного размера"""
        test_db_path = f"test_databases/test_{size}.db"
        
        if not os.path.exists(test_db_path):
            print(f"❌ Тестовая БД не найдена: {test_db_path}")
            return False
        
        # Копируем тестовую БД
        shutil.copy2(test_db_path, self.app_db_path)
        print(f"✓ Переключено на БД с {size} записями")
        return True
    
    def run_load_test(self, size, users=10, spawn_rate=5, duration=15):
        """Запуск нагрузочного теста с указанной БД"""
        
        print(f"\n{'='*60}")
        print(f"НАГРУЗОЧНОЕ ТЕСТИРОВАНИЕ С {size} ЗАПИСЯМИ")
        print(f"{'='*60}")
        
        # Переключаем на тестовую БД
        if not self.switch_to_test_db(size):
            return None
        
        # Ждем перезапуска приложения (если нужно)
        time.sleep(3)
        
        # Запускаем Locust
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        base_name = f"load_testing/results/test_{size}_{timestamp}"
        
        cmd = [
            "locust",
            "-f", "load_testing/locustfile.py",
            "--host", "http://localhost:8000",
            "--users", str(users),
            "--spawn-rate", str(spawn_rate),
            "--run-time", f"{duration}s",
            "--headless",
            "--only-summary",
            "--csv", base_name
        ]
        
        print(f"Запуск теста: {users} пользователей, {duration} секунд")
        
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=duration + 30
            )
            
            # Читаем результаты
            stats_file = f"{base_name}_stats.csv"
            if os.path.exists(stats_file):
                return {
                    'size': size,
                    'stats_file': stats_file,
                    'output': result.stdout,
                    'users': users,
                    'duration': duration
                }
            else:
                print(f"Файл результатов не найден: {stats_file}")
                return None
                
        except Exception as e:
            print(f"Ошибка при запуске теста: {e}")
            return None
    
    def run_all_tests(self):
        """Запуск всех тестов для разных объемов данных"""
        
        print("НАЧАЛО СЕРИИ НАГРУЗОЧНЫХ ТЕСТОВ")
        print("Создание резервной копии текущей БД...")
        
        # Создаем резервную копию
        self.backup_current_db()
        
        # Конфигурация тестов
        test_configs = [
            {'size': 10, 'users': 20, 'spawn_rate': 5, 'duration': 10},
            {'size': 100, 'users': 20, 'spawn_rate': 5, 'duration': 10},
            {'size': 1000, 'users': 20, 'spawn_rate': 5, 'duration': 10},
            {'size': 10000, 'users': 20, 'spawn_rate': 5, 'duration': 10},
        ]
        
        results = []
        
        for config in test_configs:
            result = self.run_load_test(
                size=config['size'],
                users=config['users'],
                spawn_rate=config['spawn_rate'],
                duration=config['duration']
            )
            
            if result:
                results.append(result)
            
            # Пауза между тестами
            time.sleep(10)
        
        # Восстанавливаем оригинальную БД
        print("\nВосстановление оригинальной БД...")
        self.restore_backup()
        
        return results
    
    def analyze_results(self, results):
        """Анализ результатов тестирования"""
        
        if not results:
            print("Нет результатов для анализа")
            return
        
        # Собираем данные
        data = []
        
        for result in results:
            stats_file = result['stats_file']
            
            if os.path.exists(stats_file):
                df = pd.read_csv(stats_file)
                aggregated = df[df['Name'] == 'Aggregated']
                
                if not aggregated.empty:
                    row = aggregated.iloc[0]
                    data.append({
                        'Размер данных': result['size'],
                        'Пользователи': result['users'],
                        'Длительность (с)': result['duration'],
                        'RPS': row['Requests/s'],
                        'Среднее время (мс)': row['Average Response Time'],
                        'Мин время (мс)': row['Min Response Time'],
                        'Макс время (мс)': row['Max Response Time'],
                        'Ошибки': row['Failure Count'],
                        'Всего запросов': row['Request Count']
                    })
        
        # Создаем DataFrame
        results_df = pd.DataFrame(data)
        
        # Сохраняем результаты
        results_df.to_csv('load_testing/results/summary.csv', index=False, encoding='utf-8')
        
        print("\nРЕЗУЛЬТАТЫ ТЕСТИРОВАНИЯ:")
        print(results_df.to_string())
        
        # Строим графики
        self.create_performance_graphs(results_df)
        
        return results_df
    
    def create_performance_graphs(self, df):
        """Создание графиков производительности"""
        
        plt.figure(figsize=(14, 10))
        
        # 1. График RPS от объема данных
        plt.subplot(2, 2, 1)
        plt.plot(df['Размер данных'], df['RPS'], 'bo-', linewidth=2, markersize=8)
        plt.xlabel('Объем данных (записей)')
        plt.ylabel('Запросов в секунду (RPS)')
        plt.title('Производительность системы')
        plt.grid(True, alpha=0.3)
        
        # Добавляем значения на точках
        for i, row in df.iterrows():
            plt.text(row['Размер данных'], row['RPS'], 
                    f"{row['RPS']:.1f}", 
                    ha='center', va='bottom')
        
        # 2. График времени ответа
        plt.subplot(2, 2, 2)
        plt.plot(df['Размер данных'], df['Среднее время (мс)'], 'ro-', 
                linewidth=2, markersize=8, label='Среднее')
        plt.plot(df['Размер данных'], df['Мин время (мс)'], 'g^--', 
                linewidth=1, markersize=6, label='Мин')
        plt.plot(df['Размер данных'], df['Макс время (мс)'], 'bs--', 
                linewidth=1, markersize=6, label='Макс')
        
        plt.xlabel('Объем данных (записей)')
        plt.ylabel('Время ответа (мс)')
        plt.title('Время ответа системы')
        plt.legend()
        plt.grid(True, alpha=0.3)
        
        # 3. График в логарифмической шкале
        plt.subplot(2, 2, 3)
        plt.loglog(df['Размер данных'], df['Среднее время (мс)'], 'go-', 
                  linewidth=2, markersize=8)
        plt.xlabel('Объем данных (log)')
        plt.ylabel('Время ответа (log, мс)')
        plt.title('Логарифмическая зависимость')
        plt.grid(True, alpha=0.3, which='both')
        
        # 4. Сводная таблица
        plt.subplot(2, 2, 4)
        plt.axis('off')
        
        # Подготавливаем данные для таблицы
        table_data = []
        for _, row in df.iterrows():
            table_data.append([
                f"{row['Размер данных']:,}".replace(',', ' '),
                f"{row['RPS']:.1f}",
                f"{row['Среднее время (мс)']:.1f}",
                f"{row['Ошибки']}"
            ])
        
        table = plt.table(
            cellText=table_data,
            colLabels=['Данные', 'RPS', 'Время(мс)', 'Ошибки'],
            cellLoc='center',
            loc='center',
            colWidths=[0.2, 0.2, 0.2, 0.2]
        )
        
        table.auto_set_font_size(False)
        table.set_fontsize(10)
        table.scale(1.2, 1.5)
        
        plt.suptitle('Результаты нагрузочного тестирования с разными объемами данных', 
                    fontsize=14, fontweight='bold')
        
        plt.tight_layout()
        plt.savefig('load_testing/results/performance_by_data_size.png', 
                   dpi=300, bbox_inches='tight')
        plt.show()
        
        print("\nГрафики сохранены в load_testing/results/performance_by_data_size.png")

def main():
    """Основная функция"""
    
    print("="*60)
    print("НАГРУЗОЧНОЕ ТЕСТИРОВАНИЕ С РАЗНЫМИ ОБЪЕМАМИ ДАННЫХ")
    print("="*60)
    
    # Проверяем что тестовые БД существуют
    if not os.path.exists("test_databases"):
        print("❌ Папка test_databases не найдена!")
        print("Сначала создайте тестовые БД:")
        print("  python load_testing/create_test_db.py")
        return
    
    # Проверяем что приложение запущено
    import requests
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code != 200:
            print("❌ Приложение не отвечает на порту 8000")
            print("Запустите: uvicorn backend.src.main:app --host 0.0.0.0 --port 8000")
            return
    except:
        print("❌ Приложение не запущено!")
        print("Запустите: uvicorn backend.src.main:app --host 0.0.0.0 --port 8000")
        return
    
    # Создаем switcher и запускаем тесты
    switcher = DatabaseSwitcher()
    results = switcher.run_all_tests()
    
    if results:
        print("\n" + "="*60)
        print("АНАЛИЗ РЕЗУЛЬТАТОВ")
        print("="*60)
        
        df = switcher.analyze_results(results)
        
        # Генерируем отчет
        generate_report(df)

def generate_report(df):
    """Генерация текстового отчета"""
    
    report = f"""
    ОТЧЕТ О НАГРУЗОЧНОМ ТЕСТИРОВАНИИ
    =================================
    Дата тестирования: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    
    ТЕСТОВАЯ СРЕДА:
    - Приложение: FastAPI
    - База данных: SQLite
    - Тестовый инструмент: Locust
    - Объемы данных: 10, 100, 1000, 10000 записей
    
    РЕЗУЛЬТАТЫ:
    """
    
    for _, row in df.iterrows():
        report += f"""
    {row['Размер данных']} записей:
      - Пользователей: {row['Пользователи']}
      - Длительность: {row['Длительность (с)']} сек
      - RPS: {row['RPS']:.2f} запросов/сек
      - Среднее время ответа: {row['Среднее время (мс)']:.2f} мс
      - Ошибки: {row['Ошибки']} ({row['Ошибки']/row['Всего запросов']*100:.2f}%)
        """
    
    # Анализ масштабируемости
    if len(df) >= 2:
        small = df.iloc[0]
        large = df.iloc[-1]
        
        rps_degradation = (small['RPS'] - large['RPS']) / small['RPS'] * 100
        time_increase = (large['Среднее время (мс)'] - small['Среднее время (мс)']) / small['Среднее время (мс)'] * 100
        
        report += f"""
    АНАЛИЗ МАСШТАБИРУЕМОСТИ:
    - Деградация RPS: {rps_degradation:.1f}%
    - Увеличение времени ответа: {time_increase:.1f}%
    
    ВЫВОДЫ:
    """
    
    # Рекомендации на основе результатов
    if rps_degradation > 50:
        report += "1. ❌ Значительная деградация производительности при увеличении данных\n"
        report += "   Рекомендации:\n"
        report += "   - Добавить индексы в БД на часто запрашиваемые поля\n"
        report += "   - Внедрить пагинацию для больших выборок\n"
        report += "   - Оптимизировать сложные запросы с JOIN\n"
    elif rps_degradation > 20:
        report += "1. ⚠️ Умеренная деградация производительности\n"
        report += "   Рекомендации:\n"
        report += "   - Рассмотреть кэширование часто запрашиваемых данных\n"
        report += "   - Оптимизировать наиболее медленные эндпоинты\n"
    else:
        report += "1. ✅ Хорошая масштабируемость системы\n"
    
    if large['Среднее время (мс)'] > 1000:
        report += "2. ❌ Время ответа превышает 1 секунду при больших данных\n"
        report += "   Рекомендации:\n"
        report += "   - Внедрить асинхронные запросы к БД\n"
        report += "   - Использовать Redis для кэширования\n"
        report += "   - Оптимизировать структуру БД\n"
    
    report += """
    ДОПОЛНИТЕЛЬНЫЕ РЕКОМЕНДАЦИИ:
    - Регулярно проводить нагрузочное тестирование
    - Настроить мониторинг производительности
    - Ведение логов медленных запросов
    - Периодическая оптимизация БД (VACUUM для SQLite)
    """
    
    # Сохраняем отчет
    with open('load_testing/results/final_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nОтчет сохранен в load_testing/results/final_report.txt")
    print(report)

if __name__ == "__main__":
    main()
