import copy


def data_pin_init(timing_data, key):
    cell_fall_data = []
    cell_rise_data = []
    fall_transition_data = []
    rise_transition_data = []

    index = [0, 0, 0, 0]
    for pin in timing_data[key]:
        # TODO: is this check necessary?
        for item in pin:
            if hasattr(item, 'cell_fall'):
                cell_fall_data.append((index[0], item.cell_fall))
                index[0] += 1
            if hasattr(item, 'cell_rise'):
                cell_rise_data.append((index[1], item.cell_rise))
                index[1] += 1
            if hasattr(item, 'fall_transition'):
                fall_transition_data.append((index[2], item.fall_transition))
                index[2] += 1
            if hasattr(item, 'rise_transition'):
                rise_transition_data.append((index[3], item.rise_transition))
                index[3] += 1

    return cell_fall_data, cell_rise_data, fall_transition_data, rise_transition_data


def table_merge(data):
    all_data = []
    temp_data = []
    names = []
    temp_dict = {}

    data_name = set()

    data = sorted(data, key=lambda x: x[0])

    for item in data:
        temp_data.append(item[1])

    data = copy.deepcopy(temp_data)
    temp_data.clear()

    left_bracket = ''
    right_bracket = ''
    tab = ''
    quotes = '\"'
    comma = ''
    line_feed = '\n'
    slash = '\\'

    for item in data:
        for name, value in item.items():
            data_name.add(name)
            all_data.append({name: value.values})

    for item in all_data:
        for name, values in item.items():
            names.append(name)

    names = list(set(names))

    for name in names:
        for item in all_data:
            if name in item.keys():
                temp_data.append(item[name])
        temp_dict[name] = temp_data
        temp_data = []

    all_data.clear()

    for name, values in temp_dict.items():
        temp_data = temp_dict[name]
        temp_value = ''

        for counter, value in enumerate(temp_data):
            if counter != 0:
                tab = '\t\t\t\t\t'

            if counter == (len(value.split(sep=',')) - 1):
                line_feed = ''
                comma = ''
                slash = ''

            temp_value = temp_value + tab + value + comma + line_feed

            tab = ''
            line_feed = '\n'

        all_data.append({name: temp_value})
    return all_data, list(data_name)


def final_pin_data(data_files):
    timing_pin_names = []
    timing_data = {}
    pins = []
    values = []
    cell_name = ''

    for lib in data_files:
        for name, value in lib.cell.items():
            if len(cell_name) == 0:
                cell_name = name
            values.append(value)

    for item in values:
        keys_pins = []
        values_pins = []
        pins_final_data = {}

        # TODO: Add this sequence as func

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
                if pin.name not in timing_data.keys():
                    pins.append(pin.name)
                    timing_data[pin.name] = []
                if pin.name in timing_data.keys():
                    if hasattr(pin, 'timing'):
                        timing_data[pin.name].append(pin.timing)

        for key in pins:
            pins_final_data[key] = timing_data[key][0]

    for key in pins:
        if hasattr(timing_data[key][0][0], 'cell_fall'):
            # TODO: maybe i should change the logic here

            cell_fall_data, cell_rise_data, fall_transition_data, rise_transition_data = data_pin_init(timing_data, key)

            cell_fall_data, cell_fall_names = table_merge(cell_fall_data)
            cell_rise_data, cell_rise_names = table_merge(cell_rise_data)
            fall_transition_data, fall_transition_names = table_merge(fall_transition_data)
            rise_transition_data, rise_transition_names = table_merge(rise_transition_data)

            for related_pin_instance in pins_final_data[key]:
                pin_template_names = []
                for template_name in related_pin_instance.cell_fall.keys():
                    pin_template_names.append(template_name)

                for pin_template_name in pin_template_names:
                    if pin_template_name in cell_fall_names \
                            and pin_template_name in related_pin_instance.cell_fall.keys():
                        for cell_related_template in cell_fall_data:
                            if pin_template_name in cell_related_template:
                                related_pin_instance.cell_fall[pin_template_name].values = \
                                    tuple(cell_related_template[pin_template_name].split())

            for related_pin_instance in pins_final_data[key]:
                pin_template_names = []
                for template_name in related_pin_instance.cell_rise.keys():
                    pin_template_names.append(template_name)

                for pin_template_name in pin_template_names:
                    if pin_template_name in cell_rise_names \
                            and pin_template_name in related_pin_instance.cell_rise.keys():
                        for cell_related_template in cell_rise_data:
                            if pin_template_name in cell_related_template:
                                related_pin_instance.cell_rise[pin_template_name].values = \
                                    tuple(cell_related_template[pin_template_name].split())

            for related_pin_instance in pins_final_data[key]:
                pin_template_names = []
                for template_name in related_pin_instance.fall_transition.keys():
                    pin_template_names.append(template_name)

                for pin_template_name in pin_template_names:
                    if pin_template_name in fall_transition_names \
                            and pin_template_name in related_pin_instance.fall_transition.keys():

                        for cell_related_template in fall_transition_data:
                            if pin_template_name in cell_related_template:
                                related_pin_instance.fall_transition[pin_template_name].values = \
                                    tuple(cell_related_template[pin_template_name].split())

            for related_pin_instance in pins_final_data[key]:
                pin_template_names = []
                for template_name in related_pin_instance.rise_transition.keys():
                    pin_template_names.append(template_name)

                for pin_template_name in pin_template_names:
                    if pin_template_name in rise_transition_names \
                            and pin_template_name in related_pin_instance.rise_transition.keys():
                        for cell_related_template in rise_transition_data:
                            if pin_template_name in cell_related_template:
                                related_pin_instance.rise_transition[pin_template_name].values = \
                                    tuple(cell_related_template[pin_template_name].split())

    for key in keys_pins:
        for obj in pins:
            if obj == values[0].pin[key].name:
                values[0].pin[key].timing[0] = pins_final_data[obj][0]

    final_data = values[0]
    return final_data
