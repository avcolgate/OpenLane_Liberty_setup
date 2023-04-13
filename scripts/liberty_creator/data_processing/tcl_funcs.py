from typing import List

def make_tcl(
    design_name: str,
    module_inputs: str,
    clocks: str,
    clock_period: str,
    path_input_lib : str,
    pin_transitions: List[float],
    clk_transitions: List[float],
    results_dir: str,
    temp_dir: str
    ) -> None:

    inputs_wo_clk = []

    clock_list = clocks.split()

    for inp in module_inputs:
        if inp not in clock_list:
            inputs_wo_clk.append(inp)

    input_str = ' '.join(inputs_wo_clk)

    # clk_tran = '%clk%'
    # pin_tran = '%pin%'

    for clk_tran in clk_transitions:
        for pin_tran in pin_transitions:

            output_tcl_name = temp_dir + '/%s_clk_%s_pin_%s.tcl' % (design_name, clk_tran, pin_tran)
            
            output_tcl = open(output_tcl_name , 'w')

            output_tcl.write('source $::env(SCRIPTS_DIR)/openroad/common/io.tcl\n')

            output_tcl.write('read_db $::env(CURRENT_ODB)\n')

            output_tcl.write('read_liberty ' + path_input_lib + '\n')
            
            for clk in clock_list:
                output_tcl.write('create_clock -name %s -period %f [get_ports {%s}]\n' % (clk, float(clock_period), clk))
                output_tcl.write('set_clock_transition %s [get_clocks {%s}]\n' % (clk_tran, clk))

            output_tcl.write('set_input_transition %s [get_ports {%s}]\n' % (pin_tran, input_str))

            if clock_list:
                output_tcl.write('write_timing_model %s/%s_clk_%s_pin_%s.lib\n\n' % (results_dir, design_name, clk_tran, pin_tran))
            else:
                output_tcl.write('write_timing_model %s/%s_clk_%s_pin_%s.lib\n\n' % (results_dir, design_name, 'NaN', pin_tran))

            # output_tcl.write('report_power > %s/%s_power.txt\n' % (results_dir, design_name))

            output_tcl.close()


    # power_tcl_name = temp_dir + '/power_%s.tcl' % (design_name)
    # power_tcl = open(power_tcl_name , 'w')
    # power_tcl.write('report power')
    # output_tcl.close()
