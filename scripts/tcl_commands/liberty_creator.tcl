
proc run_liberty_creator {args} {
    increment_index
    TIMER::timer_start

    puts_info "Running Liberty creator..." 

    if { ![file exists $::env(RESULTS_DIR)/signoff/$::env(DESIGN_NAME).lef]} {
        puts_err "LEF file doest exists in results/signoff/ ! Exiting..."
        return
    } else {
        set LEF $::env(RESULTS_DIR)/signoff/$::env(DESIGN_NAME).lef
    }

    if { ![file exists $::env(RESULTS_DIR)/synthesis/$::env(DESIGN_NAME).v]} {
        puts_err "Netlist file doest exists in results/synthesis/ ! Exiting..."
        return
    } else {
        set NETLIST $::env(RESULTS_DIR)/synthesis/$::env(DESIGN_NAME).v
    }

    set LIB_OUTPUT_DIR   $::env(RESULTS_DIR)/final/lib_lc
    file mkdir $LIB_OUTPUT_DIR

    set slowest_lib_exists [info exists ::env(LIB_SLOWEST)]
    set typical_lib_exists [info exists ::env(LIB_TYPICAL)]
    set fastest_lib_exists [info exists ::env(LIB_FASTEST)]

    if {slowest_lib_exists == 0 && typical_lib_exists == 0 && fastest_lib_exists && 0} {
        puts_err "No corners are available! Exiting..."
        return
    }

    set leakage_file [glob $::env(signoff_logs)/*_sta.log]

    if { $slowest_lib_exists } {
        puts_info "Slowest corner creating..."

        set TEMP_LIB_SLOWEST_DIR $::env(TMP_DIR)/liberty_creator/lib/slowest
        file mkdir $TEMP_LIB_SLOWEST_DIR

        set TEMP_TCL_SLOWEST_DIR $::env(TMP_DIR)/liberty_creator/tcl/slowest
        file mkdir $TEMP_TCL_SLOWEST_DIR

        set value [exec python3 $::env(SCRIPTS_DIR)/liberty_creator/process_data.py \
                $::env(DESIGN_NAME) \
                $::env(CLOCK_PORT) \
                $::env(CLOCK_PERIOD) \
                $NETLIST \
                $LEF \
                $::env(LIB_SLOWEST) \
                $TEMP_TCL_SLOWEST_DIR \
                $TEMP_LIB_SLOWEST_DIR \
        ]
        puts $value

        foreach tcl [glob $TEMP_TCL_SLOWEST_DIR/*.tcl] {
            run_openroad_script $tcl
        }

        set value [exec python3 $::env(SCRIPTS_DIR)/liberty_creator/merge_lib.py \
                    $TEMP_LIB_SLOWEST_DIR \
                    $LIB_OUTPUT_DIR \
                    $::env(CLOCK_PORT) \
                    $leakage_file \
        ]
        puts $value
    }

    if { $typical_lib_exists } {
        puts_info "Typical corner creating..."

        set TEMP_LIB_TYPICAL_DIR $::env(TMP_DIR)/liberty_creator/lib/typical
        file mkdir $TEMP_LIB_TYPICAL_DIR

        set TEMP_TCL_TYPICAL_DIR $::env(TMP_DIR)/liberty_creator/tcl/typical
        file mkdir $TEMP_TCL_TYPICAL_DIR

        set value [exec python3 $::env(SCRIPTS_DIR)/liberty_creator/process_data.py \
                $::env(DESIGN_NAME) \
                $::env(CLOCK_PORT) \
                $::env(CLOCK_PERIOD) \
                $NETLIST \
                $LEF \
                $::env(LIB_TYPICAL) \
                $TEMP_TCL_TYPICAL_DIR \
                $TEMP_LIB_TYPICAL_DIR \
        ]
        puts $value

        foreach tcl [glob $TEMP_TCL_TYPICAL_DIR/*.tcl] {
            run_openroad_script $tcl
        }

        set value [exec python3 $::env(SCRIPTS_DIR)/liberty_creator/merge_lib.py \
                    $TEMP_LIB_TYPICAL_DIR \
                    $LIB_OUTPUT_DIR \
                    $::env(CLOCK_PORT) \
                    $leakage_file \
        ]
        puts $value
    }

    if { $fastest_lib_exists } {
        puts_info "Fastest corner creating..."

        set TEMP_LIB_FASTEST_DIR $::env(TMP_DIR)/liberty_creator/lib/fastest
        file mkdir $TEMP_LIB_FASTEST_DIR

        set TEMP_TCL_FASTEST_DIR $::env(TMP_DIR)/liberty_creator/tcl/fastest
        file mkdir $TEMP_TCL_FASTEST_DIR

        set value [exec python3 $::env(SCRIPTS_DIR)/liberty_creator/process_data.py \
                $::env(DESIGN_NAME) \
                $::env(CLOCK_PORT) \
                $::env(CLOCK_PERIOD) \
                $NETLIST \
                $LEF \
                $::env(LIB_FASTEST) \
                $TEMP_TCL_FASTEST_DIR \
                $TEMP_LIB_FASTEST_DIR \
        ]
        puts $value

        foreach tcl [glob $TEMP_TCL_FASTEST_DIR/*.tcl] {
            run_openroad_script $tcl
        }

        set value [exec python3 $::env(SCRIPTS_DIR)/liberty_creator/merge_lib.py \
                    $TEMP_LIB_FASTEST_DIR \
                    $LIB_OUTPUT_DIR \
                    $::env(CLOCK_PORT) \
                    $leakage_file \
        ]
        puts $value
    }

    TIMER::timer_stop
    exec echo "[TIMER::get_runtime]" | python3 $::env(SCRIPTS_DIR)/write_runtime.py "liberty_creator - liberty_creator"
}
