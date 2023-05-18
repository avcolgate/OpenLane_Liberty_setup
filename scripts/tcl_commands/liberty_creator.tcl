
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
		puts_warn "LEF file (for size calculating) doesn't exists in '$::env(RESULTS_DIR)/signoff/$::env(DESIGN_NAME).lef'! Size will set to 1."
		set SIZE 1
	} else {
		set LEF $::env(RESULTS_DIR)/signoff/$::env(DESIGN_NAME).lef
		set SIZE [exec python3 $::env(SCRIPTS_DIR)/liberty_creator/get_size.py $LEF]
	}

	if { ![file exists $::env(signoff_logs)/28-rcx_sta.log]} {
		puts_warn "STA log (for leakage power) doesn't exists in '$::env(signoff_logs)'! Leakage power will set to 1."
		set LEAKAGE 1
	} else {
		set STA_LOG [glob $::env(signoff_logs)/*_sta.log]
		set LEAKAGE [exec python3 $::env(SCRIPTS_DIR)/liberty_creator/get_leakage.py $STA_LOG]
	}
	
	make_PVT $::env(LIB_SLOWEST) $NETLIST $SIZE $LEAKAGE
	make_PVT $::env(LIB_FASTEST) $NETLIST $SIZE $LEAKAGE
    make_PVT $::env(LIB_TYPICAL) $NETLIST $SIZE $LEAKAGE

	foreach lib $additional_libs {
		make_PVT $lib $NETLIST $SIZE $LEAKAGE
	}

	TIMER::timer_stop
	exec echo "[TIMER::get_runtime]" | python3 $::env(SCRIPTS_DIR)/write_runtime.py "liberty_creator - liberty_creator"
}


proc make_PVT {LIBRARY NETLIST SIZE LEAKAGE}  {

	if { ![file exists $LIBRARY]} {
		puts_warn "Library $LIBRARY doesn't exists! Skipping..."
		return
	}

	set CONDITIONS [exec python3 $::env(SCRIPTS_DIR)/liberty_creator/get_conditions.py $LIBRARY]
	set lib_name $CONDITIONS

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
				$SIZE \
				$CONDITIONS
	]
	if {!($mlib_status eq "")} {
		set err_msg "Error in merging lib files during making Liberty $lib_name\n$mlib_status"
		puts_err $err_msg
		return
	}
}
