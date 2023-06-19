import sys
from data_processing.lib_funcs import get_conditions

lib_file = sys.argv[1]

success, result = get_conditions(lib_file)
if not success:
    conditions = ''
    print(result)
    exit()
else:
    conditions = result

print(conditions)
