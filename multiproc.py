from multiprocessing import Process, Queue
import os
import sys

def run_script(script_name, queue):
    # Перенаправляем стандартный вывод в переменную
    sys.stdout = open(os.devnull, 'w')
    # Запускаем скрипт и сохраняем результаты его работы
    result = os.popen(f'python {script_name}').read()
    # Возвращаем стандартный вывод на место
    sys.stdout = sys.__stdout__
    # Помещаем результат в очередь
    queue.put((script_name, result))

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
        print(f'Результаты {script_name}:')
        print(result)
