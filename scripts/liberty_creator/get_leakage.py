import sys
from data_processing.leakage_funcs import get_leakage

sta_log_file = sys.argv[1]  # путь до лог-файла OpenSTA

# вызов функции извлечения значения утечки мощности
success, result = get_leakage(sta_log_file)
if not success:
    leakage = 0.0
    print(result)
    exit()
else:
    leakage = result

print(leakage)
