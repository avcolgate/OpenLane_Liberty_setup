import re
class BasicAxis:
    index_1 = ""
    name = ""
    variable_1 = ""
    index_2 = ""
    variable_2 = ""

    def __init__(self):
        self.index_1 = "0"
        self.name = "None"
        self.variable_1 = "0"
        self.index_2 = "0"
        self.variable_2 = "0"

    def axis(self, name, index_value, variable_name):
        self.name = name
        self.index_1 = index_value
        self.variable_1 = variable_name

    def add_index(self, index_value, variable_name):
        self.index_2 = index_value
        self.variable_2 = variable_name

# , indexes, values, names
def add_axis(data, input_net_transitions):

    templates = []
    basic_data_array = []
    second_axis = set()

    if hasattr(data, 'lu_table_template') == 0:
        return 0

    for item in data.lu_table_template.items():
            templates.append(item)

    for item in input_net_transitions:
        second_axis.add(item[0])

    second_axis = list(second_axis)
    second_axis.sort()
    second_axis = [float(i) for i in second_axis]
    second_axis = [str(i) + ', ' for i in second_axis]
    second_axis[-1] = second_axis[-1][:-2]
    second_axis = ''.join(second_axis)
    second_axis = second_axis

    #TODO: Remove hard-code part
    for index, item in enumerate(templates):
        basic_data_array.append(BasicAxis())
        basic_data_array[index].axis(item[0], item[1].index_1, item[1].variable_1)
        basic_data_array[index].add_index(second_axis, 'input_net_transition')

    for index in basic_data_array:
        data.lu_table_template[index.name].index_2 = index.index_2
        data.lu_table_template[index.name].variable_2 = index.variable_2


    return 1
