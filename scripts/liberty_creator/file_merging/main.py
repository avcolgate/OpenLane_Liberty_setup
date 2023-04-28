from file_merging import misc_funcs
from file_merging import axis_funcs
from copy import deepcopy



def merge_lib(data_from, data_to, clock_names, size=1.0, leakage=1.0):
    if clock_names:
        clock_names = clock_names.split()

    data_files, net_transitions = misc_funcs.data_load(data_from)
    data_files = misc_funcs.data_sort(data_files)

    if clock_names:
        data_files_scalar = misc_funcs.data_load_legacy(data_from)
        data_files_scalar = misc_funcs.data_sort_scalar(data_files_scalar)
    else:
        data_files_scalar = None


    data_template = deepcopy(data_files[0])
    temperature, voltage = misc_funcs.get_temp_volt(data_template)
    cell_name = next(iter(data_template.cell.keys()))

    pin_data, scalar_data, bus_data = misc_funcs.data_init(data_files, data_files_scalar, cell_name, clock_names)
    data_template = misc_funcs.final_merge(data_template, cell_name, pin_data, bus_data, scalar_data, clock_names)
    axis_funcs.add_axis(data_template, net_transitions)

    # data_template.cell[cell_name].pin = ''
    # data_template.cell[cell_name].bus = ''

    data_from = data_from.split('/')[-1]
    result_name = data_from + '_' + cell_name + '.lib'

    if hasattr(data_template, 'comment'):
        data_template.comment = '""'
    with open(data_to + '/' + result_name, 'w', encoding='utf-8') as final_solution:
        data_template.dump(final_solution, '')

    misc_funcs.post_formatting(data_to, result_name, cell_name, net_transitions, clock_names)

    return True



