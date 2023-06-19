from typing import Any, List, Tuple
import re


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
        if not is_template_section and line.strip().startswith('lu_table_template'):
            is_template_section = True
            template = Template()
            name = re.search('\((.+)\)', line)  # collecting name of template in parentheses
            template.name = name

        if is_template_section:
            if 'variable' in line:
                var = line[line.find(':') + 1:line.find(';')].replace('"', '').strip()
                template.variables.append(var)

            if 'index' in line:
                index_list = list()
                index_line = line[line.find('(') + 1:line.find(')')].replace('"', '').strip()
                temp_list = index_line.replace(' ', '').split(',')
                for ind in temp_list:
                    index_list.append(float(ind))
                template.indices.append(index_list)

            if '}' in line:
                is_template_section = False
                template_list.append(template)

        if 'cell(' in line.replace(' ', ''):
            break

    return template_list


def get_transitions(file_path: str) -> Tuple[bool, Any]:
    """
    Возвращает кортеж (success, result)
    При success = True, result будет содержать список значений input_net_transition   List[str]
    При success = False, result будет содержать сообщение об ошибке                   str
    """
    success = True
    result = ""

    min_value = 999999999
    template = Template()

    template_list = parse_templates(file_path)

    if not template_list:
        success = False
        result = 'No templates found in input Liberty'

    # choosing template where the maximum capacitance is minimal
    for t in template_list:
        if 'input_net_transition' in t.variables and \
                'total_output_net_capacitance' in t.variables and \
                len(t.indices) == len(t.variables) == 2:
            for num, var in enumerate(t.variables):
                if var == 'total_output_net_capacitance':
                    value = t.indices[num][-1]  # the last (max) index in line of total_output_net_capacitance
            if value < min_value:
                min_value = value
                template = t

    if not template.name and template_list:
        success = False
        result = 'No correct templates found in input Liberty'

    for num, var in enumerate(template.variables):
        if var == 'input_net_transition':
            result = template.indices[num]

    return success, result


def get_conditions(file_path: str) -> Tuple[bool, str]:
    """
    Возвращает кортеж (success, result)
    При success = True, result будет содержать строку, содержащую параметр default_operating_conditions  str
    При success = False, result будет содержать сообщение об ошибке                                      str
    """
    success = True
    result = ""

    conditions = ""

    f = open(file_path, 'r')
    for line in f:
        if line.strip().startswith('default_operating_conditions'):
            conditions = line[line.find('"') + 1:line.rfind('"')].strip()
            break

    if not conditions:
        result = "No information about default operating conditions in Library"
        success = False
    else:
        result = conditions

    return success, result

# print(get_conditions('/home/vinogradov/.volare/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib'))

# print(get_transitions('/home/vinogradov/.volare/CMOS8F_4M/libs.ref/CORELIB8DLL/liberty/nom_1.65V_25C/CORELIB8DLL.lib'))
