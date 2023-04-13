import os
from typing import List
from config import *
from data_processing.verilog_funcs import is_good_name

def data_init() -> None:

    # clock check
    try:
        for clk in clocks:
            if not is_good_name(clk):
                print("data init step:\n\tfatal: %s is bad clock name!\n\texiting" % clk)
                exit()
    except NameError:
        print("data init step:\n\tfatal: clock list is not defined in config.py! set empty list if no clocks in design\n\texiting")
        exit()

    # paths check
    try:
        if not os.path.exists(path_opensta):
            print("data init step:\n\tfatal: %s does not exist!\n\texiting" % path_opensta)
            exit()
    except NameError:
        print("data init step:\n\tfatal: path_opensta is not defined in config.py!\n\texiting")
        exit()

    try:
        if not os.path.exists(path_input_lib):
            print("data init step:\n\tfatal: %s does not exist!\n\texiting" % path_input_lib)
            exit()
    except NameError:
        print("data init step:\n\tfatal: path_input_lib is not defined in config.py!\n\texiting")
        exit()

    try:
        if not os.path.exists(path_lef):
            print("data init step:\n\tfatal: %s does not exist!\n\texiting" % path_lef)
            exit()
    except NameError:
        print("data init step:\n\tfatal: path_lef is not defined in config.py!\n\texiting")
        exit()

    try:
        if not os.path.exists(verilog_path):
            print("data init step:\n\tfatal: %s does not exist!\n\texiting" % verilog_path)
            exit()
    except NameError:
        print("data init step:\n\tfatal: path_verilog is not defined in config.py!\n\texiting")
        exit()
    
    try:
        if not os.path.exists(path_netlist):
            print("data init step:\n\tfatal: %s does not exist!\n\texiting" % path_netlist)
            exit()
    except NameError:
        print("data init step:\n\tfatal: path_netlist is not defined in config.py!\n\texiting")
        exit()

    # directories check
    try:
        clean_up_or_make(dir_results)
    except NameError:
        print("data init step:\n\tfatal: dir_results is not defined in config.py!\n\texiting")
        exit()
    try:
        clean_up_or_make(dir_temp)
    except NameError:
        print("data init step:\n\tfatal: dir_results is not defined in config.py!\n\texiting")
        exit()


def clean_up_or_make(dir_name: str, except_of: str = '') -> None:
    if os.path.exists(dir_name) and os.path.isdir(dir_name):
        for f in os.listdir(dir_name):
            if f != except_of:
                os.remove(os.path.join(dir_name, f))
    else:
        os.mkdir(dir_name)

def multirun(clk_transition: List[float], pin_transitions: List[float], dir_temp: str):
    temp_tcl_path = dir_temp + "/temp.tcl"
    for clk_t in clk_transition:
        for pin_t in pin_transitions:
            with open(file=temp_tcl_path, mode='rt') as file:
                text = file.read()
                text = text.replace("%pin%", str(pin_t))
                text = text.replace("%clk%", str(clk_t))
                exec_path = dir_temp + "/make_lib_clk_%s_pin_%s.tcl" % (clk_t, pin_t)
                with open(file=exec_path, mode="w") as file_out:
                    file_out.write(text)

                cmd = path_opensta + " -no_splash " + exec_path
                os.system(cmd)
                os.remove(exec_path)

                print("ready: clk_%s_pin_%s" % (clk_t, pin_t))
    os.remove(temp_tcl_path)