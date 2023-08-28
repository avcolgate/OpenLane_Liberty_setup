import sys
from data_processing.verilog_funcs import get_design_inputs
from data_processing.lib_funcs import get_transitions
from data_processing.tcl_funcs import make_tcl

design_name = sys.argv[1]          # имя схемы
clocks = sys.argv[2]               # строка с названиями тактовых сигналов, записанных подряд через пробел
clock_period = sys.argv[3]         # период тактового сигнала 
netlist_path = sys.argv[4]         # путь до входого Verilog файла
input_lib_path = sys.argv[5]       # путь до входого файла Liberty 
tcl_dir = sys.argv[6]              # название директории для хранения исполняемых файлов TCL
temp_lib_dir = sys.argv[7]         # название временной директории для хранения промежуточных Liberty файлов
conditions = sys.argv[8]           # строка с условиями характеризации
extra_lib_paths = sys.argv[9]      # пути до дополнительных библиотек из переменной окружения EXTRA_LIBS, записанных подряд через пробел

# вызов функции получения имен входов модуля с указанным именем
success, result = get_design_inputs(netlist_path, design_name)
if not success:
    module_inputs = []
    print(result)
    exit()
else:
    module_inputs = result

# вызов функции извлечения списка значений времени переключения входного сигнала
success, result = get_transitions(input_lib_path)
if not success:
    pin_transitions = []
    print(result)
    exit()
else:
    pin_transitions = result

# получение списка значений времени переключения тактового сигнала (при их наличии)
clk_transitions = ['NaN'] if clocks == '' else pin_transitions

# вызов функции генерации исполняемого TCL файла для генерации массива промежуточных Liberty файла 
make_tcl(design_name, module_inputs, clocks, clock_period, input_lib_path, conditions, pin_transitions,
         clk_transitions, temp_lib_dir, tcl_dir, extra_lib_paths)
