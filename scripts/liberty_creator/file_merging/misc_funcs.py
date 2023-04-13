from typing import Tuple, List, Any

from file_merging.logic.models import Liberty
from file_merging import pin_funcs
from file_merging import bus_funcs
from file_merging import scalar_funcs
import os
import re


def data_load(data_dir: str) -> Tuple[List[Any], List[Tuple[Any, ...]]]:
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
            data_files.append((float(tuple(re.findall("\d+\.\d+", file))[0]), lib))
            input_net_transitions.append(tuple(re.findall("\d+\.\d+", file)))


    # for file in temp_data:
    #     if re.search('.lib', file):
    #         input_net_transitions.append(tuple(re.findall("\d+\.\d+", file)))

    return data_files, input_net_transitions


def data_load_legacy(data_dir):
    data_files = []
    data = os.listdir(data_dir)
    input_net_transitions = []

    for count, file in enumerate(data):
        lib = Liberty.load(data_dir + '/' + data[count])

        if re.search('.lib', file):
            input_net_transitions.append(tuple(re.findall("\d+\.\d+", file)))
            data_files.append((tuple(re.findall("\d+\.\d+", file)), lib))
    return data_files


def final_merge(input_data, cell_name, pin_data, bus_data, scalar_data, clock_names='clk'):
    input_data.cell[cell_name] = scalar_data

    for pin in input_data.cell[cell_name].pin:
        if pin in clock_names:
            input_data.cell[cell_name].pin[pin].clock = 'true'

        if hasattr(input_data.cell[cell_name].pin[pin], 'timing'):
            for index, item in enumerate(input_data.cell[cell_name].pin[pin].timing):
                if hasattr(item, 'cell_fall'):
                    item.cell_fall = pin_data.pin[pin].timing[index].cell_fall
                if hasattr(item, 'cell_rise'):
                    item.cell_rise = pin_data.pin[pin].timing[index].cell_rise
                if hasattr(item, 'fall_transition'):
                    item.fall_transition = pin_data.pin[pin].timing[index].fall_transition
                if hasattr(item, 'rise_transition'):
                    item.rise_transition = pin_data.pin[pin].timing[index].rise_transition

    if hasattr(input_data.cell[cell_name], 'bus') and hasattr(bus_data, 'bus'):
        for bus in input_data.cell[cell_name].bus:
            for pin in input_data.cell[cell_name].bus[bus].pin:
                if hasattr(input_data.cell[cell_name].bus[bus].pin[pin], 'timing'):
                    for index, item in enumerate(input_data.cell[cell_name].bus[bus].pin[pin].timing):
                        if hasattr(item, 'cell_fall'):
                            item.cell_fall = bus_data.bus[bus].pin[pin].timing[index].cell_fall
                        if hasattr(item, 'cell_rise'):
                            item.cell_rise = bus_data.bus[bus].pin[pin].timing[index].cell_rise
                        if hasattr(item, 'fall_transition'):
                            item.fall_transition = bus_data.bus[bus].pin[pin].timing[index].fall_transition
                        if hasattr(item, 'rise_transition'):
                            item.rise_transition = bus_data.bus[bus].pin[pin].timing[index].rise_transition

    merged_cell = input_data
    return merged_cell


def data_init(data_files, data_files_scalar):

    pin_data = pin_funcs.final_pin_data(data_files)
    scalar_data = scalar_funcs.final_data(data_files_scalar)
    bus_data = bus_funcs.final_bus_data(data_files)

    return pin_data, scalar_data, bus_data


def post_formatting(file_name, name, input_net_transitions):
    lib = Liberty.load(file_name)

    template_counter = []
    temp_template_counter = []

    for item in lib.lu_table_template:
        template_counter.append(item)

    bus_data = lib.cell[name].bus
    pin_data = lib.cell[name].pin

    bus_keys = []
    pin_keys = []

    for bus in bus_data:
        bus_keys.append(bus)

    for pin in pin_data:
        pin_keys.append(pin)

    temp = []
    with open(file_name, 'r') as file:
        for line in file:
            if 'rise_constraint (%sample%)' in line:
                line = line.replace('%sample%', f'template_{len(template_counter)}')
                temp_template_counter.append(f'template_{len(template_counter)}')

            if 'fall_constraint (%sample%)' in line:
                line = line.replace('%sample%', f'template_{len(template_counter)}')
                temp_template_counter.append(f'template_{len(template_counter)}')

            temp.append(line)
    file.close()

    with open(file_name, 'w') as file:
        for line in temp:
            file.write(line)
    file.close()

    temp = []
    for item in input_net_transitions:
        temp.append(item[0])

    net_axis = set(temp)
    for key in lib.lu_table_template:
        template = lib.lu_table_template[key]

    template.index_2 = net_axis

    return 0


def data_sort(data):

    data = sorted(data, key= lambda x: x[0])
    temp_data = []

    for item in data:
        temp_data.append(item[1])

    data = temp_data

    return data

def data_sort_scalar(data):

    data = sorted(data, key= lambda x: (x[0][0], x[0][1]))
    temp_data = []

    for item in data:
        temp_data.append(item[1])

    data = temp_data

    return data


def get_temp_volt(data):

    temp = str(int(float(data.nom_temperature)))
    voltage = str(float(data.nom_voltage))
    voltage = voltage.replace('.', 'v')

    return temp, voltage