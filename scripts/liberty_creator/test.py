
from file_merging.merge_funcs import merge_lib
from data_processing.verilog_funcs import get_design_inputs

# module_name = get_module_name('lib_creator/get_inputs/v/spm.v')
# module_inputs = get_module_inputs('lib_creator/get_inputs/v/spm.v')

print(get_design_inputs('tests/data/source/v/d_flip_flop.v'))

merge_lib('file_merging/data/', 'file_merging/results', module_name='lib_sample', size=1000.1, leakage=2.2)

