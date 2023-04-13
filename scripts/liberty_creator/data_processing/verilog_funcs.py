import re
from typing import List
import os

class Module:
    def __init__(self, name: str = '') -> None:
        self.name = name
        self.attachments = list()
        self.called = False
        self.attach_num = 0
        self.inputs = list()
        self.content = list()

def get_design_inputs(filename: str, design_name: str) -> List[str]:
    module_list = list()
    inputs = list()

    module_list = get_modules(filename)

    for m in module_list:
        if m.name == design_name:
            design_module = m

    inputs = design_module.inputs

    return inputs


def get_modules(filename: str) -> List[Module]:
    module_list = list()

    with open(file=filename, mode='rt') as file:
        lines = file.read().split('\n')
        is_module_section = False

        for curr_line in lines:
            curr_line = skip_comment(curr_line).replace('\t', ' ')

            if curr_line == ' ' or '`define' in curr_line:
                continue

            if not is_module_section:
                if 'module' in curr_line and not 'endmodule' in curr_line:
                    module = Module()
                    is_module_section = True
                else:
                    continue

            if is_module_section:
                module.content.append(curr_line)
                if curr_line.strip().startswith('input'):
                    input_line = re.sub(r'\[[^()]*\]', '', curr_line)  # subtracting size
                    input_line = input_line.replace('wire', '').replace('reg', '')
                    inputs = input_line[input_line.find('input') + len('input'):input_line.find(';')].replace(' ', '').split(',')
                    for i in inputs:
                        if i in module.inputs:
                            print("read verilog step:\n\tfatal: duplicate input name '%s', file '%s'!\n\texiting" % (i, filename))
                            exit()
                        if not is_good_name(i):
                            print("read verilog step:\n\tfatal: bad input name '%s', file '%s'!\n\texiting" % (i, filename)),
                            exit()
                        module.inputs.append(i)

            if is_module_section and 'endmodule' in curr_line:
                is_module_section = False
                module_list.append(module)

    for mod in module_list:
        name = ''
        for string in mod.content:
            name += string
            if '(' in string:
                break
        name = name[name.find('module') + len('module'):name.find('(')].strip()  # from 'module' to (
        mod.name = name

    for x in module_list:
        for y in module_list:
            if x.name == y.name and x != y:
                print("read verilog step:\n\tfatal: duplicate module name '%s'!\n\texiting" % x.name)
                exit()

    if not module_list:
        print("read verilog step:\n\tfatal: no module in file!\n\texiting")
        exit()

    return module_list


def is_good_name(name: str) -> bool:
    # cannot be a keyword
    if name in keyword_list:
        return False

    # can include only letters, digits, _, $
    for letter in name:
        if letter.isalpha() or letter.isdigit() or letter == '_' or letter == '$':
            continue
        else:
            return False

    # starts with alpha
    if not str(name[0]).isalpha():
        return False

    # cannot start with dollar
    if str(name[0]) == '$':
        return False

    return True


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