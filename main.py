import subprocess
import concurrent.futures

def run_script(script_name):
    process = subprocess.Popen(['python', script_name], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    stdout, stderr = process.communicate()
    return stdout.decode('utf-8'), stderr.decode('utf-8')

if __name__ == "__main__":
    scripts = ['scriner.py', 'listner.py', 'broker.py']
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = [executor.submit(run_script, script) for script in scripts]
        for future in concurrent.futures.as_completed(futures):
            stdout, stderr = future.result()
            print(f"Output:\n{stdout}\n")
            if stderr:
                print(f"Error:\n{stderr}\n")
