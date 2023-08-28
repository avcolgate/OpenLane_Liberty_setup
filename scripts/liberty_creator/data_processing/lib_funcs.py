from typing import Any, List, Tuple

"""
Класс, содержащий информацию об имени, переменных и индексах шаблона из файла формата Liberty
"""
class Template:
    def __init__(self, name=''):
        self.name = name
        self.variables: List[str] = []
        self.indices: List[List[float]] = []

"""
Функция возвращает массив экземляров класса Template из файла формата Liberty
"""
def parse_templates(file_path: str) -> List[Template]:
    template_list = []
    is_template_section = False # флаг секции шаблона
    f = open(file_path, 'r')
    template = Template()
    
    for line in f:
        # проверка начала секции шаблона
        if not is_template_section and line.strip().startswith('lu_table_template'):
            is_template_section = True
            name = line[line.find('(') + 1:line.find(')')].replace('"', '').strip() # получение имени шаблона в скобках
            template = Template(name)                                               # создание экземляра очерендного шаблона

        if is_template_section:

            # обработка строки с переменной
            if 'variable' in line:
                var = line[line.find(':') + 1:line.find(';')].replace('"', '').strip()
                template.variables.append(var)

            # обработка строки с индексами переменной
            if 'index' in line:
                index_list = list()
                index_line = line[line.find('(') + 1:line.find(')')].replace('"', '').strip()
                temp_list = index_line.replace(' ', '').split(',')
                for ind in temp_list:
                    index_list.append(float(ind))
                template.indices.append(index_list)

            # проверка конца секции шаблона
            if '}' in line:
                is_template_section = False
                template_list.append(template)

        if 'cell(' in line.replace(' ', ''):
            break

    return template_list


"""
Функция возвращает кортеж (success, result)

При success = True, result будет содержать список значений времени переключения входного сигнала  input_net_transition   List[str]
При success = False, result будет содержать сообщение об ошибке                                                          str

Выбираемый шаблон для извлечения значений - шаблон, для которого максимальное
значение выходной ёмкости минимально среди всех шаблонов.
"""
def get_transitions(file_path: str) -> Tuple[bool, Any]:
    success = True
    result = ""

    min_value = 999999999
    value = min_value
    template = Template()

    # получение списка всех шаблонов из входного файла
    template_list = parse_templates(file_path)

    # обработка ошибки при отсутствии шаблонов во входном файле
    if not template_list:
        success = False
        result = 'No templates found in input Liberty'

    # выбирается шаблон, где максимальное значение ёмкости минимально
    for t in template_list:
        # поиск среди тех, которые подходят под нужный формат
        if 'input_net_transition' in t.variables and \
                'total_output_net_capacitance' in t.variables and \
                len(t.indices) == len(t.variables) == 2:
            for num, var in enumerate(t.variables):
                if var == 'total_output_net_capacitance':
                    value = t.indices[num][-1]  # последний (максимальный по значению) индекс в линии total_output_net_capacitance
            if value < min_value:
                min_value = value
                template = t # записывается подходящий шаблон

    # обработка ошибки в случае, если корректный шаблон не был найден
    if not template.name and template_list:
        success = False
        result = 'No correct templates found in input Liberty'

    for num, var in enumerate(template.variables):
        if var == 'input_net_transition':
            result = template.indices[num]

    return success, result


"""
Функция возвращает кортеж (success, result)

При success = True, result будет содержать значение параметра default_operating_conditions    str
При success = False, result будет содержать сообщение об ошибке                               str
"""
def get_conditions(file_path: str) -> Tuple[bool, str]:
    success = True
    result = ""
    conditions = ""

    f = open(file_path, 'r')
    # поиск нужной строки
    for line in f:
        if line.strip().startswith('default_operating_conditions'):
            conditions = line[line.find('"') + 1:line.rfind('"')].strip()
            break

    # обработка ошибки в случае, если искомая строка не найдена
    if not conditions:
        result = "No information about default operating conditions in Library"
        success = False
    else:
        result = conditions

    return success, result

# print(get_conditions('/home/vinogradov/.volare/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__tt_025C_1v80.lib'))

# print(get_transitions('/home/vinogradov/.volare/CMOS8F_4M/libs.ref/CORELIB8DLL/liberty/nom_1.65V_25C/CORELIB8DLL.lib'))

# print(get_transitions('/home/avc/.volare/sky130A/libs.ref/sky130_fd_sc_hd/lib/sky130_fd_sc_hd__ff_n40C_1v56.lib'))
