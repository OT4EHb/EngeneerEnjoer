# load_testing/quick_test.py
import subprocess
import time
import webbrowser
import os

def run_quick_test():
    """Быстрый тест с веб-интерфейсом"""
    
    print("Запуск быстрого нагрузочного теста...")
    print("После запуска откроется веб-интерфейс по адресу: http://localhost:8089")
    print("\nПараметры теста:")
    print("- Количество пользователей: 10")
    print("- Скорость роста: 1 пользователь/сек")
    print("- Хост: http://localhost:8000")
    
    # Команда для запуска Locust с веб-интерфейсом
    cmd = [
        "locust",
        "-f", "load_testing/locustfile.py",
        "--host", "http://localhost:8000",
        "--web-host", "0.0.0.0",
        "--web-port", "8089"
    ]
    
    print(f"\nЗапуск команды: {' '.join(cmd)}")
    print("\nДля остановки теста нажмите Ctrl+C в этом окне")
    
    # Пауза для запуска браузера
    time.sleep(2)
    
    # Открываем веб-интерфейс
    webbrowser.open("http://localhost:8089")
    
    # Запускаем Locust
    try:
        subprocess.run(cmd)
    except KeyboardInterrupt:
        print("\nТест остановлен пользователем")

if __name__ == "__main__":
    run_quick_test()
