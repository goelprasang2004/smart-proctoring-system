import os
import shutil

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKUP_DIR = os.path.join(BASE_DIR, 'old_flask_backup')

if not os.path.exists(BACKUP_DIR):
    os.makedirs(BACKUP_DIR)

# List of items to move
items_to_move = ['api', 'config', 'database', 'middleware', 'models', 'services', 'utils']
files_to_move = [f for f in os.listdir(BASE_DIR) if f.endswith('.py') and f != 'cleanup.py']

print(f"Moving content to {BACKUP_DIR}...")

for item in items_to_move:
    src = os.path.join(BASE_DIR, item)
    dst = os.path.join(BACKUP_DIR, item)
    if os.path.exists(src):
        print(f"Moving {item}...")
        if os.path.exists(dst):
            shutil.rmtree(dst)  # Remove existing backup if exists to avoid conflict
        shutil.move(src, dst)

for file in files_to_move:
    src = os.path.join(BASE_DIR, file)
    dst = os.path.join(BACKUP_DIR, file)
    print(f"Moving {file}...")
    shutil.move(src, dst)

print("Cleanup complete.")
