from file_merging import misc_funcs
from file_merging import axis_funcs
from copy import deepcopy


def merge_lib(data_from, data_to, clock_names='clk', size=1.0, leakage=1.0):
    clock_names = clock_names.split()
    data_files, net_transitions = misc_funcs.data_load(data_from)
    data_files = misc_funcs.data_sort(data_files)
    data_files_scalar = misc_funcs.data_load_legacy(data_from)
    data_files_scalar = misc_funcs.data_sort_scalar(data_files_scalar)
    data_template = deepcopy(data_files[0])
    temperature, voltage = misc_funcs.get_temp_volt(data_template)
    cell_name = next(iter(data_template.cell.keys()))

    pin_data, scalar_data, bus_data = misc_funcs.data_init(data_files, data_files_scalar)
    data_template = misc_funcs.final_merge(data_template, cell_name, pin_data, bus_data, scalar_data, clock_names)
    axis_funcs.add_axis(data_template, net_transitions)

    # data_template.cell[cell_name].pin = ''
    # data_template.cell[cell_name].bus = ''

    with open(data_to + '/' + cell_name + '_' + temperature + 'C_' + voltage + '.lib', 'w', encoding='utf-8') as final_solution:
        data_template.dump(final_solution, '')

    # misc_funcs.post_formatting(data_to + '/' + 'final_solution' + '.lib', 'lib_sample', net_transitions)
    return True



