import sys
from data_processing.leakage_funcs import get_leakage

sta_log_file = sys.argv[1]

success, result = get_leakage(sta_log_file)
if not success:
    print(result)
    exit()
else:
    leakage = result

print(leakage)