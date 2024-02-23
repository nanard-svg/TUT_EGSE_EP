onbreak {quit -f}
onerror {quit -f}

vsim  -lib xil_defaultlib raw_data_fifo_opt

set NumericStdNoWarnings 1
set StdArithNoWarnings 1

do {wave.do}

view wave
view structure
view signals

do {raw_data_fifo.udo}

run 1000ns

quit -force
