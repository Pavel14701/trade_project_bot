from pathlib import Path

# Получаем текущую директорию (где запущен скрипт)
current_dir = Path.cwd()

# Удаляем последний компонент из пути
parent_dir = current_dir.parent

# Преобразуем путь в строку с двойными слешами
parent_dir_str = parent_dir.as_posix()

print(parent_dir_str)
