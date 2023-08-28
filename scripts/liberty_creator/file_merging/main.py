from file_merging import misc_funcs
from file_merging import axis_funcs
from file_merging import merging
from file_merging.logic.models import Liberty


def merge_lib(data_from, data_to, clock_names= [], size=-1.0, leakage=-1.0, conditions='nothing yet'):
    """
    Main function that execute merge method.
    data_from: data input directory
    data_to: data output directory
    clock_names: list of clock names
    size: size of an area
    leakage: power leakage
    conditions: Useless now, but added for possible future changes.

    """

    if clock_names:
        clock_names = clock_names.split()

    data_files, net_transitions = misc_funcs.data_load(data_from)

    tmp_list = []
    for trans in net_transitions:
        tmp_list.append(trans)
    net_transitions = tmp_list

    indices = merging.parse_indices(data_from)
    merging.merge(data_from, data_to, indices, net_transitions)

    data_template = Liberty.load(data_to + '/tmp.lib')
    temperature, voltage = misc_funcs.get_temp_volt(data_template)
    cell_name = next(iter(data_template.cell.keys()))
    if clock_names != []:
        axis_funcs.add_axis(data_template, net_transitions)

    data_from = data_from.split('/')[-1]
    result_name = data_from + '_' + cell_name + '.lib'

    if hasattr(data_template, 'comment'):
        data_template.comment = '""'
    with open(data_to + '/' + result_name, 'w', encoding='utf-8') as final_solution:
        data_template.dump(final_solution, '')

    misc_funcs.post_formatting(data_to, result_name, cell_name, net_transitions, clock_names,
                               temperature, voltage, size, leakage)

    # print(data_to + '/' + result_name)

    merging.tmp_clr(data_to=data_to)

    return True


# merge_lib('data/ss_100C_1v60',
#           'results')
