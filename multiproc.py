from multiprocessing import Process, Queue
import os
import sys
from io import StringIO

def run_script(script_name, queue):
    # Создаем временный файл для стандартного вывода
    temp_stdout = StringIO()
    # Перенаправляем стандартный вывод в временный файл
    sys.stdout = temp_stdout
    # Запускаем скрипт
    os.system(f'python {script_name}')
    # Возвращаем стандартный вывод на место
    sys.stdout = sys.__stdout__
    # Получаем содержимое временного файла
    output = temp_stdout.getvalue()
    # Закрываем временный файл
    temp_stdout.close()
    # Помещаем результат в очередь
    queue.put((script_name, output))

if __name__ == "__main__":
    # Список скриптов для запуска
    scripts = ['main.py', 'scriner.py']
    # Создаем очередь для хранения результатов
    queue = Queue()
    # Создаем и запускаем процессы
    processes = []
    for script in scripts:
        p = Process(target=run_script, args=(script, queue))
        p.start()
        processes.append(p)
    # Ждем завершения всех процессов
    for p in processes:
        p.join()
    # Выводим результаты работы скриптов
    while not queue.empty():
        script_name, result = queue.get()
