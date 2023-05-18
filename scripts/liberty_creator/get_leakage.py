import sys
from data_processing.leakage_funcs import get_leakage

sta_log_file = sys.argv[1]

leakage = get_leakage(sta_log_file)

print(leakage)