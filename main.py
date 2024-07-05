import multiprocessing
import importlib.util

def run_script(script_name):
    try:
        spec = importlib.util.spec_from_file_location("custom_module", script_name)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module.some_function()  # Замените на имя функции, которую вы хотите вызвать
    except Exception as e:
        return None, str(e)

if __name__ == "__main__":
    scripts = ['scriner.py', 'listner.py', 'broker.py']
    with multiprocessing.Pool() as pool:
        results = pool.map(run_script, scripts)
        for stdout, stderr in results:
            if stdout is not None:
                print(f"Output:\n{stdout}\n")
            if stderr:
                print(f"Error:\n{stderr}\n")