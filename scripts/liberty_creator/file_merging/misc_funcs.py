from typing import Tuple, List, Any

from file_merging.logic.models import Liberty
from data_processing.lib_funcs import get_leakage_power_unit
import os
import re
import copy


def data_load(data_dir: str) -> Tuple[List[Any], List[Tuple[Any, ...]]]:
    """
    Return tuple of data files and net transition.
    Data_dir: String path to data directory.
    """
    data_files = list()
    data = list()
    temp_data = os.listdir(data_dir)
    input_net_transitions = []

    for t_file in temp_data:
        name, ext = os.path.splitext(t_file)
        if ext != '.lib':
            continue

        clk, clk_val, pin, pin_val = name[name.find('clk'):].split('_')

        if clk_val == 'NaN':
            data.append(t_file)
        else:
            if clk_val == pin_val:
                data.append(t_file)

    for count, file in enumerate(data):
        lib = Liberty.load(data_dir + '/' + data[count])
        if re.search('.lib', file):
            data_files.append(lib)
            input_net_transitions.append(tuple(re.findall("\d+\.\d+", file)))

    return data_files, input_net_transitions


def data_load_legacy(data_dir):
    """
    Legacy data load. Useful for tests.
    """
    data_files = []
    data = os.listdir(data_dir)
    input_net_transitions = []

    for count, file in enumerate(data):
        lib = Liberty.load(data_dir + '/' + data[count])

        if re.search('.lib', file):
            input_net_transitions.append(tuple(re.findall("\d+\.\d+", file)))
            data_files.append((tuple(re.findall("\d+\.\d+", file)), lib))
    return data_files


def get_temp_volt(data):
    """
    Parse data for temperature and voltage.
    data: template of .lib
    """

    temp = str(int(float(data.nom_temperature)))
    voltage = str(float(data.nom_voltage))
    voltage = voltage.replace('.', 'v')

    return temp, voltage


def post_formatting(data_to, result_name, name, input_net_transitions, clk_names, temperature, volt, size, leak):
    """
    Formatting dumped .lib.
    Also add a structure with a size area size, cell_leakage_power, operating_conditions,
    process  type (hard-coded) 1.0, voltage, temperature and tree_type (hard-coded) "balanced_tree"

    data_to: Output directory
    result_name: Name of the dump
    name:
    input_net_transitions: net transitions
    clk_names: list of clocks
    temperature: temperature
    volt: voltage
    size: size of an area
    leak: leaking data

    """
    file_name = data_to + '/' + result_name
    lib = Liberty.load(file_name)

    template_counter = []
    temp_template_counter = []

    pin_data = []
    bus_data = []

    if hasattr(lib.cell[name], 'bus'):
        bus_data = lib.cell[name].bus
    if hasattr(lib.cell[name], 'pin'):
        pin_data = lib.cell[name].pin

    bus_keys = []
    pin_keys = []

    for bus in bus_data:
        bus_keys.append(bus)

    for pin in pin_data:
        pin_keys.append(pin)

    with open(file_name, 'r') as file:
        for line in file:
            if 'template_' in line:
                template_counter.append(line)
    file.close()

    for item in template_counter:
        temp_template_counter += re.findall(r'\d+', item)

    template_counter = set(temp_template_counter)

    temp = []
    flag = False

    temperature = float(temperature)
    volt = float(volt.replace('v', '.'))

    success, result = get_leakage_power_unit(file_name)
    if not success:
        leakage_power_unit = ''
        print(result)
        exit()
    else:
        leakage_power_unit = result

        prefix = leakage_power_unit[leakage_power_unit.find('1')+1:leakage_power_unit.find('W')]
        prefix_to_mul = float(prefix_dict.get(prefix, 'Неизвестная единица измерения leakage_power_unit'))
        prefix_to_mul = '{0:.30f}'.format(prefix_to_mul)

    cell_leakage_power = float(leak) / float(prefix_to_mul)

    with open(file_name, 'r') as file:
        for line in file:
            if flag:
                temporary = line
                line = f'area : {size};' + '\n' + \
                       f'cell_leakage_power : {cell_leakage_power};' + '\n' + \
                       'operating_conditions' + ' ' + f'({name}_{temperature}C_{volt}' + 'VV)' + '{ \n' + \
                       f'process     :   1.0;' + '\n' + \
                       f'voltage     :   {volt};' + '\n' + \
                       f'temperature :    {temperature};' + '\n' + \
                       f'tree_type   : "balanced_tree";' + '\n' \
                       + '}' + '\n' + temporary
                flag = False

            if 'rise_constraint (%sample%)' in line:
                line = line.replace('%sample%', f'template_{len(template_counter) + 1}')

            if 'fall_constraint (%sample%)' in line:
                line = line.replace('%sample%', f'template_{len(template_counter) + 1}')

            if 'library_features' in line:
                line = ''

            if 'nom_voltage' in line:
                flag = True

            temp.append(line)
    file.close()

    with open(file_name, 'w') as file:
        for line in temp:
            file.write(line)
    file.close()

    for key in lib.lu_table_template:
        template = copy.deepcopy(lib.lu_table_template[key])

    if clk_names:
        temp = []
        for item in input_net_transitions:
            temp.append(item[0])

        net_ax = sorted(temp, key=lambda x: float(x))
        temp = ''

        for num in net_ax:
            temp += num + ', '
        temp = temp[0:-2]

        net_ax = temp

        net_ax = '"' + net_ax + '"'
        net_ax = net_ax.replace(',', '')
        net_ax = net_ax.split()
        if hasattr(template, 'index_2'):
            template.index_2 = tuple(net_ax)
        template.index_1 = tuple(net_ax)
        template.variable_1 = 'constrained_pin_transition'
        template.variable_2 = 'related_pin_transition'

        template.name = f'template_{len(template_counter) + 1}'

    lib = Liberty.load(file_name)

    for key in lib.lu_table_template:
        temp = tuple(lib.lu_table_template[key].index_1.split())
        temp_name = lib.lu_table_template[key].variable_1

        if hasattr(template, 'index_2'):
            lib.lu_table_template[key].index_1 = tuple(lib.lu_table_template[key].index_2.split())
            lib.lu_table_template[key].index_2 = temp

        if hasattr(template, 'index_2'):
            lib.lu_table_template[key].variable_1 = lib.lu_table_template[key].variable_2.split()
            lib.lu_table_template[key].variable_1 = temp_name

    if clk_names:
        lib.lu_table_template[template.name] = template

    lib.comment = '""'

    # print('AAAAA\n' + lib.nom_temperature + '\n' + lib.nom_voltage + '\nAAAAAAAAAAAAA')

    # lib.nom_temperature = float(temperature)
    # volt = volt.replace('v', '.')
    # lib.nom_voltage = float(volt)

    with open(data_to + '/' + result_name, 'w', encoding='utf-8') as final_solution:
        lib.dump(final_solution, '')

    return 0

def post_post_formatting(data_to, result_name):
    temp = []
    file_name = data_to + '/' + result_name
    with open(file_name, 'r') as file:
        for line in file:
            if 'related_pin' in line:
                line = line.split()
                line[0] = '\t\t' + line[0] + ' '
                line[-1] = ' "' + line[-1][0:-1] + '";\n'
                line = ''.join(line)

            temp.append(line)
        file.close()

    with open(file_name, 'w') as file:
        for line in temp:
            file.write(line)
    file.close()


prefix_dict = {'y': 1e-24,  # yocto
           'z': 1e-21,  # zepto
           'a': 1e-18,  # atto
           'f': 1e-15,  # femto
           'p': 1e-12,  # pico
           'n': 1e-9,   # nano
           'u': 1e-6,   # micro
           'm': 1e-3,   # mili
           'c': 1e-2,   # centi
           'd': 1e-1,   # deci
           'k': 1e3,    # kilo
           'M': 1e6,    # mega
           'G': 1e9,    # giga
           'T': 1e12,   # tera
           'P': 1e15,   # peta
           'E': 1e18,   # exa
           'Z': 1e21,   # zetta
           'Y': 1e24,   # yotta
    }