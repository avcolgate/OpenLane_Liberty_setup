import sys
from data_processing.lib_funcs import get_conditions

lib_file = sys.argv[1] # путь до Liberty файла угла

# вызов функции извлечения строки с условиями характеризации
success, result = get_conditions(lib_file)
if not success:
    conditions = ''
    print(result)
    exit()
else:
    conditions = result

print(conditions)
