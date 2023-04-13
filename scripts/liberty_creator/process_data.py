import sys

from data_processing.verilog_funcs import get_design_inputs
from data_processing.lef_funcs import get_size
from data_processing.lib_funcs import get_transitions
from data_processing.tcl_funcs import make_tcl

design_name = sys.argv[1]
clocks = sys.argv[2]
clock_period = sys.argv[3]
verilog_path = sys.argv[4]
path_lef = sys.argv[5]
path_input_lib = sys.argv[6]
dir_temp = sys.argv[7]
results_dir = sys.argv[8]

module_inputs = get_design_inputs(verilog_path, design_name)

module_size = get_size(path_lef)

pin_transitions = get_transitions(path_input_lib)
clk_transitions = ['NaN'] if clocks == '' else pin_transitions

make_tcl(design_name, module_inputs, clocks, clock_period, path_input_lib, pin_transitions, clk_transitions, results_dir, dir_temp)
