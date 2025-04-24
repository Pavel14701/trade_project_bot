import multiprocessing
import os

def run_script(script_name):
    os.system(f'python {script_name}')

if __name__ == '__main__':
    scripts = [
        'scriner/scriner.py',
        'listner.py',
        'broker.py'
    ]
    
    processes = []
    
    for script in scripts:
        p = multiprocessing.Process(target=run_script, args=(script,))
        processes.append(p)
        p.start()
    
    for p in processes:
        p.join()
