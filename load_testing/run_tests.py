# load_testing/run_tests.py
import subprocess
import time
import os
import sys
from datetime import datetime
import json
import matplotlib.pyplot as plt
import pandas as pd

def ensure_app_running():
    """Проверка, что приложение запущено"""
    import requests
    try:
        response = requests.get("http://localhost:8000/", timeout=5)
        if response.status_code == 200:
            print("✓ Приложение запущено на http://localhost:8000")
            return True
    except requests.ConnectionError:
        print("✗ Приложение не запущено!")
        print("Запустите приложение в отдельном терминале:")
        print("  uvicorn backend.src.main:app --host 0.0.0.0 --port 8000")
        return False

def run_single_test(test_name, users, spawn_rate, duration, data_size=""):
    """Запуск одного теста Locust"""
    
    print(f"\n{'='*60}")
    print(f"Тест: {test_name}")
    print(f"Пользователи: {users}, Скорость: {spawn_rate}/сек, Длительность: {duration}сек")
    print(f"{'='*60}")
    
    # Создаем уникальное имя для файлов результатов
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    base_name = f"results/{test_name}_{timestamp}"
    
    # Команда для запуска Locust
    cmd = [
        "locust",
        "-f", "load_testing/locustfile.py",
        "--host", "http://localhost:8000",
        "--users", str(users),
        "--spawn-rate", str(spawn_rate),
        "--run-time", f"{duration}s",
        "--headless",
        "--only-summary",
        "--csv", base_name,
        "--html", f"{base_name}.html"
    ]
    
    if data_size:
        base_name = f"{base_name}_{data_size}"
    
    print(f"Запуск команды: {' '.join(cmd)}")
    print("Тестирование запущено...")
    
    start_time = time.time()
    
    # Запускаем Locust
    try:
        result = subprocess.run(
            cmd, 
            capture_output=True, 
            text=True, 
            timeout=duration + 30
        )
        
        if result.returncode != 0:
            print(f"Ошибка при выполнении теста:")
            print(result.stderr)
            return None
        
        # Читаем результаты из CSV
        stats_file = f"{base_name}_stats.csv"
        if os.path.exists(stats_file):
            return {
                "test_name": test_name,
                "users": users,
                "spawn_rate": spawn_rate,
                "duration": duration,
                "data_size": data_size,
                "stats_file": stats_file,
                "html_report": f"{base_name}.html",
                "output": result.stdout
            }
        else:
            print(f"Файл результатов не найден: {stats_file}")
            return None
            
    except subprocess.TimeoutExpired:
        print("Тест превысил максимальное время выполнения")
        return None
    
    except Exception as e:
        print(f"Ошибка: {e}")
        return None

def run_test_series():
    """Запуск серии тестов с разными параметрами"""
    
    # Создаем папку для результатов
    os.makedirs("load_testing/results", exist_ok=True)
    
    # Конфигурация тестов
    test_scenarios = [
        # Название теста, пользователей, скорость роста, длительность, объем данных
        {"name": "Низкая нагрузка", "users": 10, "spawn_rate": 1, "duration": 60},
        {"name": "Средняя нагрузка", "users": 50, "spawn_rate": 5, "duration": 120},
        {"name": "Высокая нагрузка", "users": 100, "spawn_rate": 10, "duration": 180},
        {"name": "Пиковая нагрузка", "users": 200, "spawn_rate": 20, "duration": 240},
    ]
    
    # Для разных объемов данных
    data_sizes = ["10", "100", "1000", "10000"]
    
    results = []
    
    print("="*60)
    print("НАГРУЗОЧНОЕ ТЕСТИРОВАНИЕ ПРИЛОЖЕНИЯ")
    print("="*60)
    
    # Проверяем, что приложение запущено
    if not ensure_app_running():
        return
    
    # Запускаем тесты для каждого объема данных
    for data_size in data_sizes:
        print(f"\n\n{'#'*60}")
        print(f"ТЕСТИРОВАНИЕ С {data_size} ЗАПИСЯМИ В БД")
        print(f"{'#'*60}")
        
        # TODO: Здесь нужно загрузить тестовые данные нужного объема
        # load_test_data(data_size)
        
        # Пауза для стабилизации БД
        time.sleep(5)
        
        # Запускаем все сценарии для этого объема данных
        for scenario in test_scenarios:
            result = run_single_test(
                test_name=f"{scenario['name']}_{data_size}",
                users=scenario['users'],
                spawn_rate=scenario['spawn_rate'],
                duration=scenario['duration'],
                data_size=data_size
            )
            
            if result:
                results.append(result)
            
            # Пауза между тестами
            time.sleep(10)
    
    return results

def analyze_results(results):
    """Анализ результатов тестирования и построение графиков"""
    
    if not results:
        print("Нет результатов для анализа")
        return
    
    # Собираем все данные
    all_stats = []
    
    for result in results:
        stats_file = result['stats_file']
        if os.path.exists(stats_file):
            df = pd.read_csv(stats_file)
            
            # Находим общую статистику
            total_stats = df[df['Name'] == 'Aggregated'].iloc[0]
            
            all_stats.append({
                'test_name': result['test_name'],
                'data_size': result['data_size'],
                'users': result['users'],
                'rps': total_stats['Requests/s'],
                'avg_response_time': total_stats['Average Response Time'],
                'min_response_time': total_stats['Min Response Time'],
                'max_response_time': total_stats['Max Response Time'],
                'failures': total_stats['Failure Count'],
                'failure_rate': total_stats['Failure Count'] / total_stats['Request Count'] * 100
            })
    
    # Создаем DataFrame
    stats_df = pd.DataFrame(all_stats)
    
    # Сохраняем сводную таблицу
    stats_df.to_csv('load_testing/results/summary.csv', index=False)
    
    print("\n" + "="*60)
    print("СВОДНАЯ ТАБЛИЦА РЕЗУЛЬТАТОВ")
    print("="*60)
    print(stats_df.to_string())
    
    # Строим графики
    create_plots(stats_df)
    
    # Генерируем отчет
    generate_report(stats_df)

def create_plots(df):
    """Создание графиков производительности"""
    
    plt.figure(figsize=(15, 10))
    
    # 1. График RPS в зависимости от нагрузки и объема данных
    plt.subplot(2, 2, 1)
    for data_size in df['data_size'].unique():
        subset = df[df['data_size'] == data_size]
        plt.plot(subset['users'], subset['rps'], 'o-', label=f"{data_size} записей")
    
    plt.xlabel('Количество пользователей')
    plt.ylabel('Запросов в секунду (RPS)')
    plt.title('Производительность системы')
    plt.legend()
    plt.grid(True)
    
    # 2. График времени ответа
    plt.subplot(2, 2, 2)
    for data_size in df['data_size'].unique():
        subset = df[df['data_size'] == data_size]
        plt.plot(subset['users'], subset['avg_response_time'], 's-', label=f"{data_size} записей")
    
    plt.xlabel('Количество пользователей')
    plt.ylabel('Среднее время ответа (мс)')
    plt.title('Время ответа системы')
    plt.legend()
    plt.grid(True)
    
    # 3. График процента ошибок
    plt.subplot(2, 2, 3)
    for data_size in df['data_size'].unique():
        subset = df[df['data_size'] == data_size]
        plt.plot(subset['users'], subset['failure_rate'], '^-', label=f"{data_size} записей")
    
    plt.xlabel('Количество пользователей')
    plt.ylabel('Процент ошибок (%)')
    plt.title('Стабильность системы')
    plt.legend()
    plt.grid(True)
    
    # 4. Сравнение производительности для разных объемов данных
    plt.subplot(2, 2, 4)
    
    # Группируем по объему данных
    grouped = df.groupby('data_size')['rps'].mean()
    
    bars = plt.bar(grouped.index.astype(str), grouped.values)
    plt.xlabel('Объем данных (записей)')
    plt.ylabel('Средний RPS')
    plt.title('Влияние объема данных на производительность')
    
    # Добавляем значения на столбцы
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height,
                f'{height:.1f}', ha='center', va='bottom')
    
    plt.tight_layout()
    
    # Сохраняем графики
    plt.savefig('load_testing/results/performance_graphs.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("\nГрафики сохранены в load_testing/results/performance_graphs.png")

def generate_report(df):
    """Генерация текстового отчета"""
    
    report = f"""
    ОТЧЕТ О НАГРУЗОЧНОМ ТЕСТИРОВАНИИ
    =================================
    Дата тестирования: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
    Всего проведено тестов: {len(df)}
    
    ОБЩАЯ СТАТИСТИКА:
    - Максимальный RPS: {df['rps'].max():.2f} запросов/сек
    - Минимальное время ответа: {df['avg_response_time'].min():.2f} мс
    - Максимальное время ответа: {df['avg_response_time'].max():.2f} мс
    - Средний процент ошибок: {df['failure_rate'].mean():.2f}%
    
    РЕЗУЛЬТАТЫ ПО ОБЪЕМАМ ДАННЫХ:
    """
    
    for data_size in sorted(df['data_size'].unique()):
        subset = df[df['data_size'] == data_size]
        report += f"""
    {data_size} записей:
      - Средний RPS: {subset['rps'].mean():.2f}
      - Среднее время ответа: {subset['avg_response_time'].mean():.2f} мс
      - Максимальная нагрузка: {subset['users'].max()} пользователей
      - Процент ошибок: {subset['failure_rate'].mean():.2f}%
        """
    
    report += f"""
    ВЫВОДЫ И РЕКОМЕНДАЦИИ:
    """
    
    # Анализ результатов
    if df['failure_rate'].max() > 5:
        report += "1. Высокий процент ошибок (>5%) при нагрузке. Необходимо:\n"
        report += "   - Увеличить лимиты соединений с БД\n"
        report += "   - Оптимизировать медленные запросы\n"
        report += "   - Рассмотреть горизонтальное масштабирование\n"
    
    if df['avg_response_time'].max() > 1000:
        report += "2. Время ответа превышает 1 секунду. Рекомендации:\n"
        report += "   - Добавить индексы в БД на часто используемые поля\n"
        report += "   - Внедрить кэширование (Redis)\n"
        report += "   - Оптимизировать сложные JOIN-запросы\n"
    
    # Анализ масштабируемости
    small_data = df[df['data_size'] == '10']
    large_data = df[df['data_size'] == '10000']
    
    if not small_data.empty and not large_data.empty:
        perf_degradation = (small_data['rps'].mean() - large_data['rps'].mean()) / small_data['rps'].mean() * 100
        report += f"3. Деградация производительности при увеличении данных: {perf_degradation:.1f}%\n"
        
        if perf_degradation > 50:
            report += "   - Значительная деградация! Необходимо:\n"
            report += "     * Пересмотреть структуру БД\n"
            report += "     * Внедрить пагинацию\n"
            report += "     * Оптимизировать запросы с большими выборками\n"
    
    report += """
    ДОПОЛНИТЕЛЬНЫЕ РЕКОМЕНДАЦИИ:
    - Регулярно проводить нагрузочное тестирование
    - Мониторить производительность в production
    - Настроить алертинг при превышении порогов
    """
    
    # Сохраняем отчет
    with open('load_testing/results/performance_report.txt', 'w', encoding='utf-8') as f:
        f.write(report)
    
    print(f"\nОтчет сохранен в load_testing/results/performance_report.txt")
    
    # Выводим отчет в консоль
    print(report)

if __name__ == "__main__":
    print("Нагрузочное тестирование приложения")
    print("Для начала убедитесь, что приложение запущено:")
    print("  uvicorn backend.src.main:app --host 0.0.0.0 --port 8000")
    print("\nНажмите Enter для продолжения...")
    input()
    
    # Запускаем тесты
    results = run_test_series()
    
    # Анализируем результаты
    if results:
        analyze_results(results)
