import re
from typing import Any, Tuple

"""
Класс, содержащий информацию об имени и входах модуля из Verilog файла
"""
class Module:
    def __init__(self, name: str = '') -> None:
        self.name = name
        self.inputs = list()


"""
Функция получения имен входов модуля с указанным именем

Возвращает кортеж (success, result)
При success = True, result будет содержать список имен искомого модуля   List[str]
При success = False, result будет содержать сообщение об ошибке          str
"""
def get_design_inputs(filename: str, design_name: str) -> Tuple[bool, Any]:
    success = True # флаг успешного выполнения функции
    result = ""
    is_comment_block = False # флаг блока комментариев
    module = Module()

    with open(file=filename, mode='rt') as file:
        lines = file.read().split('\n')
        is_module_section = False # флаг блока искомого модуля

        for curr_line in lines:
            curr_line = skip_comment(curr_line) # пропуск комментариев в конце строки 

            if curr_line.strip().startswith('`define'): # пропуск конструкции define
                continue

            # обработка блока с комментариями
            if '/*' in curr_line and not is_comment_block:
                is_comment_block = True

            # обработка блока с комментариями
            if '*/' in curr_line and is_comment_block:
                is_comment_block = False
                continue

            # проверка начала секции модуля 
            if not is_module_section and not is_comment_block:
                if curr_line.strip().startswith('module ' + design_name):
                    module.name = design_name
                    is_module_section = True
                else:
                    continue

            # обработка строк, содержащих входы
            if is_module_section and not is_comment_block:
                if curr_line.strip().startswith('input'):
                    input_line = curr_line.strip().replace('input', '')
                    input_line_wo_size = re.sub(r'\[[^()]*]', '', input_line)  # subtracting size
                    input_line_wo_size = input_line_wo_size.replace('wire', '').replace('reg', '')
                    inputs = re.sub("[ ;]", "", input_line_wo_size).split(',')

                    # добавление имен в массив имен, обработка ошибок
                    for i in inputs:
                        if i in module.inputs:
                            success = False
                            result = "Input name '%s' has a duplicate, in file '%s'" % (i, filename)
                            break
                        if not is_good_name(i):
                            success = False
                            result = "Bad input name '%s', in file '%s'" % (i, filename)
                            break
                        module.inputs.append(i)

            # проверка конца секции модуля 
            if is_module_section and curr_line.strip().startswith('endmodule') and not is_comment_block:
                is_module_section = False

    # обработка случая, когда искомый модуль не найден
    if not module.name:
        success = False
        result = "No module in file '%s'" % filename

    # обработка случая, когда искомый модуль не имеет входов
    if not module.inputs and module.name:
        success = False
        result = "No inputs in module '%s'" % design_name

    if success:
        result = module.inputs

    return success, result


"""
Функция, проверяющая имена на корректность
"""
def is_good_name(name: str) -> bool:
    # имя не может быть ключевым словом
    if name in keyword_list:
        return False

    # может содержать только буквы, цифры, _, $
    for letter in name:
        if letter.isalpha() or letter.isdigit() or letter == '_' or letter == '$':
            continue
        else:
            return False

    # начинается с буквы
    if not str(name[0]).isalpha():
        return False

    # не начинается с $
    if str(name[0]) == '$':
        return False

    return True


"""
Функция, пропускающая комментарии в конце строки
"""
def skip_comment(line: str) -> str:
    if '//' in line:
        line = line[:line.find('//')]
    return line


keyword_list = ['above', 'abs', 'absdelay', 'ac_stim', 'acos', 'acosh', 'always', 'analog', 'analysis', 'and', 'asin',
                'asinh', 'assign', 'atan', 'atan2', 'atanh', 'begin', 'branch', 'buf', 'bufif0', 'bufif1', 'case',
                'casex', 'casez', 'ceil', 'cmos', 'connectrules', 'cos', 'cosh', 'cross', 'ddt', 'deassign', 'default',
                'defparam', 'disable', 'discipline', 'driver_update', 'edge', 'else', 'end', 'endcase',
                'endconnectrules', 'enddiscipline', 'endfunction', 'endmodule', 'endnature', 'endprimitive',
                'endspecify', 'endtable', 'endtask', 'event', 'exclude', 'exp', 'final_step', 'flicker_noise', 'flow',
                'for', 'force', 'forever', 'fork', 'from', 'function', 'generate', 'genvar', 'ground', 'highz0',
                'highz1', 'hypot', 'idt', 'idtmod', 'if', 'ifnone', 'inf', 'initial', 'initial_step', 'inout', 'input',
                'integer', 'join', 'laplace_nd', 'laplace_np', 'laplace_zd', 'laplace_zp', 'large', 'last_crossing',
                'limexp', 'ln', 'log', 'macromodule', 'max', 'medium', 'min', 'module', 'nand', 'nature', 'negedge',
                'net_resolution', 'nmos', 'noise_table', 'nor', 'not', 'notif0', 'notif1', 'or', 'output', 'parameter',
                'pmos', 'posedge', 'potential', 'pow', 'primitive', 'pull0', 'pull1', 'pulldown', 'pullup', 'rcmos',
                'real', 'realtime', 'reg', 'release', 'repeat', 'rnmos', 'rpmos', 'rtran', 'rtranif0', 'rtranif1',
                'scalared', 'sin', 'sinh', 'slew', 'small', 'specify', 'specparam', 'sqrt', 'strong0', 'strong1',
                'supply0', 'supply1', 'table', 'tan', 'tanh', 'task', 'time', 'timer', 'tran', 'tranif0', 'tranif1',
                'transition', 'tri', 'tri0', 'tri1', 'triand', 'trior', 'trireg', 'vectored', 'wait', 'wand', 'weak0',
                'weak1', 'while', 'white_noise', 'wire', 'wor', 'wreal', 'xnor', 'xor', 'zi_nd', 'zi_np', 'zi_zd',
                'zi_zp']
