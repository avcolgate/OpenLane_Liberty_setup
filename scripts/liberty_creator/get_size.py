import sys
from data_processing.lef_funcs import get_size

lef_file = sys.argv[1]

size = get_size(lef_file)

print(size)