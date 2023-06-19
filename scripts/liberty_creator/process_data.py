import sys

from data_processing.verilog_funcs import get_design_inputs
from data_processing.lib_funcs import get_transitions
from data_processing.tcl_funcs import make_tcl

design_name = sys.argv[1]
clocks = sys.argv[2]
clock_period = sys.argv[3]
netlist_path = sys.argv[4]
input_lib_path = sys.argv[5]
tcl_dir = sys.argv[6]
temp_lib_dir = sys.argv[7]
conditions = sys.argv[8]
extra_lib_paths = sys.argv[9]

success, result = get_design_inputs(netlist_path, design_name)
if not success:
    module_inputs = []
    print(result)
    exit()
else:
    module_inputs = result

success, result = get_transitions(input_lib_path)
if not success:
    pin_transitions = []
    print(result)
    exit()
else:
    pin_transitions = result

clk_transitions = ['NaN'] if clocks == '' else pin_transitions

make_tcl(design_name, module_inputs, clocks, clock_period, input_lib_path, conditions, pin_transitions,
         clk_transitions, temp_lib_dir, tcl_dir, extra_lib_paths)
