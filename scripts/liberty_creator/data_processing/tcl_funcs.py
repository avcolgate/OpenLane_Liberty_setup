from typing import List

def make_tcl(
    design_name: str,
    module_inputs: str,
    clocks: str,
    clock_period: str,
    path_input_lib : str,
    conditions: str,
    pin_transitions: List[float],
    clk_transitions: List[float],
    temp_lib_dir: str,
    tcl_dir: str,
    extra_lib_paths: List[str]
    ) -> None:

    clock_list = clocks.split()

    extra_lib_list = extra_lib_paths.split()

    for clk in clock_list:
        module_inputs.remove(clk)

    inputs_line = ' '.join(module_inputs)

    tcl_filename = tcl_dir + '/%s_%s.tcl' % (design_name, conditions)

    output_tcl = open(tcl_filename , 'w')

    output_tcl.write('source $::env(SCRIPTS_DIR)/openroad/common/io.tcl\n')

    output_tcl.write('read_db $::env(CURRENT_ODB)\n')

    output_tcl.write('read_liberty ' + path_input_lib + '\n')

    for lib in extra_lib_list:
        output_tcl.write('read_liberty ' + lib + '\n')

    for clk in clock_list:
        output_tcl.write('create_clock -name %s -period %f [get_ports {%s}]\n' % (clk, float(clock_period), clk))
        

    for clk_tran in clk_transitions:
        for in_tran in pin_transitions:
            
            output_tcl.write('\nset_input_transition %s [get_ports {%s}]\n' % (in_tran, inputs_line))

            if clock_list:
                output_tcl.write('set_clock_transition %s [get_clocks {%s}]\n' % (clk_tran, clocks))
            else:
                clk_tran = 'NaN'

            output_tcl.write('write_timing_model %s/%s_%s_clk_%s_pin_%s.lib\n' % (temp_lib_dir, design_name, conditions, clk_tran, in_tran))

    
    output_tcl.close()
