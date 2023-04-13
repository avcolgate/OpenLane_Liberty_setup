import sys
from file_merging.main import merge_lib
from data_processing.leakage_funcs import get_leakage

data_from = sys.argv[1]
data_to = sys.argv[2]
clock_names = sys.argv[3]
leakage_file = sys.argv[4]

module_leakage = get_leakage(leakage_file)

merge_lib(data_from=data_from, data_to=data_to, clock_names=clock_names, size=0.1, leakage=module_leakage)

