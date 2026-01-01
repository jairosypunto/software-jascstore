import os
from collections import defaultdict

# Ruta raíz del proyecto
root_dir = "."

# Diccionario para agrupar por nombre de archivo
duplicates = defaultdict(list)

# Buscar archivos .css
for dirpath, _, filenames in os.walk(root_dir):
    for filename in filenames:
        if filename.endswith(".css"):
            full_path = os.path.join(dirpath, filename)
            duplicates[filename].append(full_path)

# Mostrar duplicados
print("\n🔍 Archivos CSS duplicados:\n")
for name, paths in duplicates.items():
    if len(paths) > 1:
        print(f"{name} ({len(paths)} copias):")
        for path in paths:
            print(f"  - {path}")
        print()