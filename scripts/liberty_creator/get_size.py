import sys
from data_processing.lef_funcs import get_size

lef_file = sys.argv[1] # путь до LEF файла

# вызов функции извлечения значения размера ячейки
success, result = get_size(lef_file)
if not success:
    size = 0.0
    print(result)
    exit()
else:
    size = float(result)

print(size)
