import sys
from data_processing.lef_funcs import get_size

lef_file = sys.argv[1]

success, result = get_size(lef_file)
if not success:
    size = 0.0
    print(result)
    exit()
else:
    size = result

print(size)
