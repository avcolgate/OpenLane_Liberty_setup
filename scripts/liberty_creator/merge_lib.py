import sys
from file_merging.main import merge_lib

data_from = sys.argv[1]     # название папки с массивом промежуточных Liberty файлов
data_to = sys.argv[2]       # название папки с конечным Liberty файлом
clock_names = sys.argv[3]   # строка с именами тактовых сигналов
leakage = sys.argv[4]       # значение утечки мощности
size = sys.argv[5]          # значение размера ячейки
conditions = sys.argv[6]    # значение параметра default_operating_conditions

# вызов функции объединения промежуточных Liberty файлов
merge_lib(data_from=data_from, data_to=data_to, clock_names=clock_names, size=size, leakage=leakage, conditions=conditions) # type: ignore
