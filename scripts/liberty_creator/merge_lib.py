import sys
from file_merging.main import merge_lib
from data_processing.leakage_funcs import get_leakage
from data_processing.lef_funcs import get_size

data_from = sys.argv[1]
data_to = sys.argv[2]
clock_names = sys.argv[3]
leakage = sys.argv[4]
size = sys.argv[5]
conditions = sys.argv[6]

merge_lib(data_from=data_from, data_to=data_to, clock_names=clock_names, size=size, leakage=leakage, conditions=conditions)

