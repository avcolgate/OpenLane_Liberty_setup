
proc run_liberty_creator {additional_libs} {
	increment_index
	TIMER::timer_start

	puts_info "Running Liberty creator..." 

	if { ![file exists $::env(RESULTS_DIR)/synthesis/$::env(DESIGN_NAME).v]} {
		puts_err "Netlist file doesn't exists in '$::env(RESULTS_DIR)/synthesis/$::env(DESIGN_NAME).v'! Exiting..."
		return
	} else {
		set NETLIST $::env(RESULTS_DIR)/synthesis/$::env(DESIGN_NAME).v
	}

	if { ![file exists $::env(RESULTS_DIR)/signoff/$::env(DESIGN_NAME).lef]} {
		puts_err "LEF file (for size calculating) doesn't exists in '::env(RESULTS_DIR)/signoff/$::env(DESIGN_NAME).lef'! Exiting..."
		return
	} else {
		set LEF $::env(RESULTS_DIR)/signoff/$::env(DESIGN_NAME).lef
	}

	if { ![file exists [glob $::env(signoff_logs)/*_sta.log]]} {
		puts_err "STA log (for leakage power) doesn't exists in '$::env(signoff_logs)'! Exiting..."
		return
	} else {
		set LEAKAGE [glob $::env(signoff_logs)/*_sta.log]
	}
	
	make_PVT $::env(LIB_SLOWEST) $NETLIST $LEF $LEAKAGE
	make_PVT $::env(LIB_FASTEST) $NETLIST $LEF $LEAKAGE
    make_PVT $::env(LIB_TYPICAL) $NETLIST $LEF $LEAKAGE

	foreach lib $additional_libs {
		make_PVT $lib $NETLIST $LEF $LEAKAGE
	}

	TIMER::timer_stop
	exec echo "[TIMER::get_runtime]" | python3 $::env(SCRIPTS_DIR)/write_runtime.py "liberty_creator - liberty_creator"
}


proc make_PVT {LIBRARY NETLIST LEF LEAKAGE}  {

	if { ![file exists $LIBRARY]} {
		puts_warn "Library $LIBRARY doesn't exists! Skipping..."
		return
	}

    set lib_name_dot_ext [lindex [split $LIBRARY '/'] end]
    set lib_name         [lindex [split $lib_name_dot_ext '.'] end-1]

    set LIB_TEMP_DIR $::env(TMP_DIR)/liberty_creator/lib/$lib_name
    set TCL_TEMP_DIR $::env(TMP_DIR)/liberty_creator/tcl/$lib_name
    set LIB_FINAL_DIR $::env(RESULTS_DIR)/final/lib

	file mkdir $LIB_TEMP_DIR $TCL_TEMP_DIR $LIB_FINAL_DIR

	set pdata_status [exec python3 $::env(SCRIPTS_DIR)/liberty_creator/process_data.py \
			$::env(DESIGN_NAME) \
			$::env(CLOCK_PORT) \
			$::env(CLOCK_PERIOD) \
			$NETLIST \
			$LIBRARY \
			$TCL_TEMP_DIR \
			$LIB_TEMP_DIR \
	]
	if {!($pdata_status eq "")} {
		set err_msg "Error in data processing during making Liberty $lib_name\n$pdata_status"
		puts_err $err_msg
		return
	}

	foreach tcl [glob $TCL_TEMP_DIR/*.tcl] {
		run_openroad_script $tcl
	}
	
	set mlib_status [exec python3 $::env(SCRIPTS_DIR)/liberty_creator/merge_lib.py \
				$LIB_TEMP_DIR \
				$LIB_FINAL_DIR \
				$::env(CLOCK_PORT) \
				$LEAKAGE \
				$LEF
	]
	if {!($mlib_status eq "")} {
		set err_msg "Error in merging lib files during making Liberty $lib_name\n$mlib_status"
		puts_err $err_msg
		return
	}
}
