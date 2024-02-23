onbreak {quit -f}
onerror {quit -f}

vsim -voptargs="+acc "  -L xpm -L fifo_generator_v13_2_7 -L xil_defaultlib -L unisims_ver -L unimacro_ver -L secureip -lib xil_defaultlib xil_defaultlib.fifo_pipe_in_w32_1024_r32_1024 xil_defaultlib.glbl

set NumericStdNoWarnings 1
set StdArithNoWarnings 1

do {wave.do}

view wave
view structure
view signals

do {fifo_pipe_in_w32_1024_r32_1024.udo}

run 1000ns

quit -force
