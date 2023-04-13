from typing import List

class Template:
    def __init__(self, name=''):
        self.name = name
        self.variables: List[str] = []
        self.indices: List[List[float]] = []

def parse_templates(file_path: str) -> List[Template]:
    template_list = []
    is_template_section = False
    f = open(file_path, 'r')

    for line in f:
        if not is_template_section and 'lu_table_template' in line:
            is_template_section = True
            template = Template()
            name = line[line.find('(')+1:line.find(')')].replace('"', '').strip()
            template.name  = name

        if is_template_section and template:
            if 'variable' in line:
                var = line[line.find(':')+1:line.find(';')].replace('"', '').strip()
                template.variables.append(var)

            if 'index' in line:
                index_list = list()
                index_line = line[line.find('(')+1:line.find(')')].replace('"', '').strip()
                temp_list = index_line.replace(' ', '').split(',')
                for ind in temp_list:
                    index_list.append(float(ind))
                template.indices.append(index_list)

            if '}' in line:
                is_template_section = False
                template_list.append(template)

        if 'cell(' in line.replace(' ', ''): #! temp
            break

    if not template_list:
        print('get transition step:\n\tfatal: no templates found in input Liberty!\n\texiting')
        exit()

    return template_list


def get_transitions(file_path: str) -> List[float]:
    min_value = 9999999
    template = None

    template_list = parse_templates(file_path)

    # choosing template where the maximum capacitance is minimal
    for templ in template_list:
        if 'input_net_transition' in templ.variables and 'total_output_net_capacitance' in templ.variables and \
                                                                len(templ.indices) == len(templ.variables) == 2:
            for num, var in enumerate(templ.variables):
                if var == 'total_output_net_capacitance':
                    value = templ.indices[num][-1] # the last (max) index in line of total_output_net_capacitance
            if value < min_value:
                min_value = value
                template = templ

    if template is None:
        print('get transition step:\n\tfatal: no correct templates found in input Liberty!\n\texiting')
        exit()

    for num, var in enumerate(template.variables):
        if var == 'input_net_transition':
            transition_list = template.indices[num]

    return transition_list
