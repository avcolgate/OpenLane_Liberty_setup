
proc run_liberty_creator {additional_libs} {
	increment_index
	TIMER::timer_start

	puts_info "Running Liberty creator..." 

	# Обработка ошибки в случае отсутствия Verilog файла синтезированного нетлиста, полученного после этапа логического синтеза
	if { ![file exists $::env(RESULTS_DIR)/synthesis/$::env(DESIGN_NAME).v]} {
		puts_err "Netlist file doesn't exists in '$::env(RESULTS_DIR)/synthesis/$::env(DESIGN_NAME).v'! Exiting..."
		return
	} else {
		set NETLIST $::env(RESULTS_DIR)/synthesis/$::env(DESIGN_NAME).v
	}

	# Обработка ошибки в случае отсутствия LEF файла
	if { ![file exists $::env(RESULTS_DIR)/signoff/$::env(DESIGN_NAME).lef]} {
		puts_warn "LEF file (for size calculating) doesn't exists in '$::env(RESULTS_DIR)/signoff/$::env(DESIGN_NAME).lef'! Size will be set to 1."
		set SIZE 1
	} else {
		set LEF $::env(RESULTS_DIR)/signoff/$::env(DESIGN_NAME).lef
		set SIZE [exec python3 $::env(SCRIPTS_DIR)/liberty_creator/get_size.py $LEF]
	}

	# Обработка ошибки в случае отсутствия LEF файла
	if { ![file exists [glob $::env(signoff_logs)/*_sta.log]]} {
		puts_warn "STA log (for leakage power) doesn't exists in '$::env(signoff_logs)'! Leakage power will be set to 1."
		set LEAKAGE 1
	} else {
		set STA_LOG [glob $::env(signoff_logs)/*_sta.log]
		set LEAKAGE [exec python3 $::env(SCRIPTS_DIR)/liberty_creator/get_leakage.py $STA_LOG]
	}

	# инициализация переменной EXTRA_LIBRARIES из переменной окружения ::env(EXTRA_LIBS)
	if { [info exists ::env(EXTRA_LIBS)]} {
		set EXTRA_LIBRARIES $::env(EXTRA_LIBS)
	} else {
		set EXTRA_LIBRARIES ""
	}
	
	# вызов функции генерации Liberty файла для угла LIB_SLOWEST при его наличии
	if { [info exists ::env(LIB_SLOWEST)]} {
		make_PVT $::env(LIB_SLOWEST) $NETLIST $SIZE $LEAKAGE $EXTRA_LIBRARIES
	}

	# вызов функции генерации Liberty файла для угла LIB_FASTEST при его наличии
	if { [info exists ::env(LIB_FASTEST)]} {
		make_PVT $::env(LIB_FASTEST) $NETLIST $SIZE $LEAKAGE $EXTRA_LIBRARIES
	}

	# вызов функции генерации Liberty файла для угла LIB_TYPICAL при его наличии
	if { [info exists ::env(LIB_TYPICAL)]} {
		make_PVT $::env(LIB_TYPICAL) $NETLIST $SIZE $LEAKAGE $EXTRA_LIBRARIES
	}

	# вызов функции генерации Liberty файла для каждого из дополнительных углов, передынных в данную функцию
	foreach lib $additional_libs {
		make_PVT $lib $NETLIST $SIZE $LEAKAGE $EXTRA_LIBRARIES
	}

	TIMER::timer_stop
	exec echo "[TIMER::get_runtime]" | python3 $::env(SCRIPTS_DIR)/write_runtime.py "liberty_creator - liberty_creator"
}


proc make_PVT {LIBRARY NETLIST SIZE LEAKAGE EXTRA_LIBRARIES}  {

	# Обработка ошибки в случае отсутствия очередного угла, для которого выполняется генерация Liberty файла
	if { ![file exists $LIBRARY]} {
		puts_warn "Library $LIBRARY doesn't exists! Skipping..."
		return
	}

	# получение значения условий характеризации строки default_operating_conditions из файла очередного угла
	set CONDITIONS [exec python3 $::env(SCRIPTS_DIR)/liberty_creator/get_conditions.py $LIBRARY]

	set lib_name $CONDITIONS

    set LIB_TEMP_DIR $::env(TMP_DIR)/liberty_creator/lib/$lib_name
    set TCL_TEMP_DIR $::env(TMP_DIR)/liberty_creator/tcl/$lib_name
    set LIB_FINAL_DIR $::env(RESULTS_DIR)/final/lib

	file mkdir $LIB_TEMP_DIR $TCL_TEMP_DIR $LIB_FINAL_DIR

	# вызов Python скрипта генерации исполняемого TCL файла для генерации массива промежуточных Liberty файла и обработка ошибок
	set pdata_status [exec python3 $::env(SCRIPTS_DIR)/liberty_creator/process_data.py \
			$::env(DESIGN_NAME) \
			$::env(CLOCK_PORT) \
			$::env(CLOCK_PERIOD) \
			$NETLIST \
			$LIBRARY \
			$TCL_TEMP_DIR \
			$LIB_TEMP_DIR \
			$CONDITIONS \
			$EXTRA_LIBRARIES \
	]
	if {!($pdata_status eq "")} {
		set err_msg "Error in data processing during making Liberty $lib_name\n$pdata_status"
		puts_err $err_msg
		return
	}

	# запуск исполняемого TCL файла 
	foreach tcl [glob $TCL_TEMP_DIR/*.tcl] {
		run_openroad_script $tcl
	}
	
	# вызов Python скрипта объединения массива промежуточных Liberty файлов в конечный Liberty файл, постформатирования и обработка ошибок
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
