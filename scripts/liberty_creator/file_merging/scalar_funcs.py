import copy
import math

def pin_data_init(timing_data, key):
    rise_constraint_data = {}
    fall_constraint_data = {}

    i = 0
    for pin in timing_data[key]:
        for item in pin:
            if hasattr(item, 'rise_constraint'):
                if i not in rise_constraint_data:
                    rise_constraint_data[i] = []
                item.rise_constraint['scalar'].name = '%sample%'
                rise_constraint_data[i].append(item.rise_constraint)
            if hasattr(item, 'fall_constraint'):
                if i not in fall_constraint_data:
                    fall_constraint_data[i] = []
                item.fall_constraint['scalar'].name = '%sample%'
                fall_constraint_data[i].append(item.fall_constraint)

            i = i + 1
        i = 0
    return rise_constraint_data, fall_constraint_data
def bus_data_init(timing_data, related_keys):
    rise_constraint_data = {}
    fall_constraint_data = {}

    for key in related_keys:
        timing = timing_data[key]
        for instance in timing:
            for index, item in enumerate(instance):
                if key not in rise_constraint_data:
                    rise_constraint_data[key] = {}
                if index not in rise_constraint_data[key]:
                    rise_constraint_data[key][index] = []
                if hasattr(item, 'rise_constraint'):
                    item.rise_constraint['scalar'].name = '%sample%'
                    rise_constraint_data[key][index].append(item.rise_constraint['scalar'].values)

                if key not in fall_constraint_data:
                    fall_constraint_data[key] = {}
                if index not in fall_constraint_data[key]:
                    fall_constraint_data[key][index] = []
                if hasattr(item, 'fall_constraint'):
                    item.fall_constraint['scalar'].name = '%sample%'
                    fall_constraint_data[key][index].append(item.fall_constraint['scalar'].values)

    return rise_constraint_data, fall_constraint_data
def merge_pins(data):
    all_data = []
    all_data_values = []
    comma = ','
    line_feed = ''
    left_bracket = '"'
    right_bracket = ''
    tab = ''
    slash = ''

    for scalar_table in data:
        keys = scalar_table.keys()
        for key in keys:
            all_data_values.append(scalar_table[key].values)

    for i, table in enumerate(all_data_values):
        all_data_values[i] = str.split(table)

    if len(all_data_values) != 0:
        temp_size = len(all_data_values[0])
    else:
        return all_data

    size_of_scalar_data = len(all_data_values)

    size_of_scalar_data = int(math.ceil(math.sqrt(size_of_scalar_data)))

    temp = ''
    i = 1
    for item in all_data_values:
        for scalar in item:
            if i == 1:
                left_bracket = '"'
            if (i % (size_of_scalar_data)) == 1 and i >= size_of_scalar_data:
                tab = '\t\t\t\t'
            if (i % (size_of_scalar_data)) == 0 and i >= size_of_scalar_data:
                line_feed = '\n'
                comma = ''
                slash = '\\'
            if i == len(all_data_values) - 1:
                line_feed = ''
                right_bracket = '"'

            temp += tab + scalar + comma + line_feed

            i += 1
            left_bracket = ''
            right_bracket = ''
            comma = ','
            tab = ''
            slash = ''
            line_feed = ''
    all_data_values = temp

    all_data = all_data_values
    return all_data

def merge_bus(data):
    all_data = []
    all_data_values = []
    comma = ','
    line_feed = ''
    left_bracket = '"'
    right_bracket = ''
    tab = ''
    slash = ''

    size_of_scalar_data = len(data[0])
    size_of_scalar_data = int(math.ceil(math.sqrt(size_of_scalar_data)))

    for item in data.values():
        all_data_values.append(item)
    temp = ''

    i = 1
    for item in all_data_values:
        for scalar in item:
            if i == 1:
                left_bracket = '"'
            if (i % (size_of_scalar_data)) == 1 and i >= size_of_scalar_data:
                tab = '\t\t\t\t'
                left_bracket = '"'
            if (i % (size_of_scalar_data)) == 0 and i >= size_of_scalar_data:
                line_feed = '\n'
                slash = '\\'
                right_bracket = '"'
                comma = ''
            if i == len(data[0]):
                comma = ''
                line_feed = ''
                right_bracket = '"'
                slash = ''

            temp += tab + scalar + comma + line_feed

            left_bracket = ''
            right_bracket = ''
            comma = ','
            tab = ''
            slash = ''
            line_feed = ''
            i += 1
        i = 1
        all_data.append(temp)
        temp = ''


    return all_data

def final_data(data_files):
    values = []
    final_data = []
    cell_name = ''

    timing_data = {}
    timing_pin_names = []

    pins = []

    timing_data_bus = {}

    for lib in data_files:
        for name, value in lib.cell.items():
            if len(cell_name) != 0:
                pass
            else:
                cell_name = name
            values.append(value)

    # Bus
    if hasattr(values[0], 'bus'):
        for item in values:
            keys_bus = []
            keys_bus_related_pins = []
            values_bus = []
            bus_final_data = {}

            for name, value in item.bus.items():
                keys_bus.append(name)
                values_bus.append(value)

            for key in keys_bus:
                for value in values_bus:
                    if value.name == key:
                        if hasattr(value, 'pin'):
                            for related_pin in value.pin:
                                if hasattr(value.pin[related_pin], 'timing'):
                                    keys_bus_related_pins.append(related_pin)
                    keys_bus_related_pins = list(set(keys_bus_related_pins))

            for bus in values_bus:
                for pin in bus.pin:
                    temp_pin = bus.pin
                    if temp_pin[pin].name in keys_bus_related_pins:
                        if hasattr(temp_pin[pin], 'timing'):
                            if temp_pin[pin].name not in timing_data_bus.keys():
                                keys_bus_related_pins.append(temp_pin[pin].name)
                                timing_data_bus[temp_pin[pin].name] = []
                            if temp_pin[pin].name in timing_data_bus.keys():
                                timing_data_bus[temp_pin[pin].name].append(temp_pin[pin].timing)

            for key in keys_bus:
                bus_final_data[key] = {}
                for pin_key in keys_bus_related_pins:
                    bus_final_data[key][pin_key] = timing_data_bus[pin_key][0]

        bus_rise_constraint, bus_fall_constraint = bus_data_init(timing_data_bus, keys_bus_related_pins)
        for key in keys_bus:
            for related_key in keys_bus_related_pins:
                if hasattr(bus_final_data[key][related_key][0], 'rise_constraint')\
                        or hasattr(bus_final_data[key][related_key][0], 'fall_constraint'):
                    bus_rise_constraint_data = merge_bus(bus_rise_constraint[related_key])
                    bus_fall_constraint_data = merge_bus(bus_fall_constraint[related_key])

                    for iteration in range(0, len(bus_rise_constraint_data)):
                        if related_key in values[0].bus[key].pin:
                            if hasattr(values[0].bus[key].pin[related_key].timing[iteration], 'rise_constraint'):
                                    if 'scalar' in values[0].bus[key].pin[related_key].timing[iteration].rise_constraint:
                                        values[0].bus[key].pin[related_key].timing[iteration].rise_constraint['scalar']\
                                            .values = tuple(copy.deepcopy(bus_rise_constraint_data[iteration].split()))

                    for iteration in range(0, len(bus_fall_constraint_data)):
                        if related_key in values[0].bus[key].pin:
                            if hasattr(values[0].bus[key].pin[related_key].timing[iteration], 'fall_constraint'):
                                    if 'scalar' in values[0].bus[key].pin[related_key].timing[iteration].fall_constraint:
                                        values[0].bus[key].pin[related_key].timing[iteration].fall_constraint['scalar']\
                                            .values = tuple(copy.deepcopy(bus_fall_constraint_data[iteration].split()))


    if hasattr(values[0], 'pin'):
    # Pin
        for item in values:
            keys_pins = []
            values_pins = []
            pins_final_data = {}

            for name, value in item.pin.items():
                keys_pins.append(name)
                values_pins.append(value)

            for key in keys_pins:
                for value in values_pins:
                    if value.name == key:
                        if hasattr(value, 'timing'):
                            timing_pin_names.append(value.name)
                    timing_pin_names = list(set(timing_pin_names))

            for pin in values_pins:
                if pin.name in timing_pin_names:
                    if hasattr(pin, 'timing'):
                        if pin.name not in timing_data.keys():
                            pins.append(pin.name)
                            timing_data[pin.name] = []
                        if pin.name in timing_data.keys():
                            timing_data[pin.name].append(pin.timing)

            for key in pins:
                pins_final_data[key] = timing_data[key][0]

        for key in pins:
            if hasattr(timing_data[key][0][0], 'rise_constraint') or hasattr(timing_data[key][0][0], 'fall_constraint'):
                rise_constraint_data, fall_constraint_data = pin_data_init(timing_data, key)

                merged_rise = {}
                for i, instance in rise_constraint_data.items():
                    merged_rise[i] = merge_pins(instance).split()

                merged_fall = {}
                for i, instance in fall_constraint_data.items():
                    merged_fall[i] = merge_pins(instance).split()

                for iteration in range(0, len(merged_rise)):
                    if hasattr(values[0].pin[key].timing[iteration], 'rise_constraint'):
                        if 'scalar' in values[0].pin[key].timing[iteration].rise_constraint:
                            values[0].pin[key].timing[iteration].rise_constraint['scalar'].values \
                                = tuple(copy.deepcopy(merged_rise[iteration]))

                for iteration in range(0, len(merged_fall)):
                    if hasattr(values[0].pin[key].timing[iteration], 'fall_constraint'):
                        if 'scalar' in values[0].pin[key].timing[iteration].fall_constraint:
                            values[0].pin[key].timing[iteration].fall_constraint['scalar'].values \
                                = tuple(copy.deepcopy(merged_fall[iteration]))



    final_data = values[0]
    return final_data
