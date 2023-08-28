from typing import Any, List

"""
Функция генерации исполняемого TCL файла для генерации массива промежуточных Liberty файла 
"""
def make_tcl(
        design_name: str,                 # имя схемы
        module_inputs: List[str],         # массив названий входов схемы 
        clocks: str,                      # строка с названиями тактовых сигналов, записанных подряд через пробел
        clock_period: str,                # период тактового сигнала 
        path_input_lib: str,              # путь до входого файла Liberty 
        conditions: str,                  # строка с условиями характеризации
        pin_transitions: List[float],     # массив значений времени переключения входных сигналов 
        clk_transitions: Any,             # массив значений времени переключения тактовых сигналов 
        temp_lib_dir: str,                # название временной директории для хранения промежуточных Liberty файлов
        tcl_dir: str,                     # название директории для хранения исполняемых файлов TCL
        extra_lib_paths: str              # пути до дополнительных библиотек из переменной окружения EXTRA_LIBS, записанных подряд через пробел
) -> None:
    clock_list = clocks.split()

    extra_lib_list = extra_lib_paths.split()

    for clk in clock_list:
        module_inputs.remove(clk)
    inputs_line = ' '.join(module_inputs)

    tcl_filename = tcl_dir + '/%s_%s.tcl' % (design_name, conditions)
    output_tcl = open(tcl_filename, 'w')

    # Инициализация базы данных
    output_tcl.write('source $::env(SCRIPTS_DIR)/openroad/common/io.tcl\n')
    output_tcl.write('read_db $::env(CURRENT_ODB)\n')

    # Чтение Liberty файла соответствующего угла
    output_tcl.write('read_liberty ' + path_input_lib + '\n')

    # Чтение дополтнительных Liberty файлов, указанных в конфугирационном файле проекта
    for lib in extra_lib_list:
        output_tcl.write('read_liberty ' + lib + '\n')

    # Создание тактовых сигналов при их наличии
    for clk in clock_list:
        output_tcl.write('create_clock -name %s -period %f [get_ports {%s}]\n' % (clk, float(clock_period), clk))

    # Установка значений времени переключения входного сигнала и тактового сигнала для всех их сочетаний 
    for clk_tran in clk_transitions:
        for in_tran in pin_transitions:

            output_tcl.write('\nset_input_transition %s [get_ports {%s}]\n' % (in_tran, inputs_line))

            if clock_list:
                output_tcl.write('set_clock_transition %s [get_clocks {%s}]\n' % (clk_tran, clocks))
            else:
                clk_tran = 'NaN'

            output_tcl.write('write_timing_model %s/%s_%s_clk_%s_pin_%s.lib\n' % (
                temp_lib_dir, design_name, conditions, clk_tran, in_tran))

    output_tcl.close()
