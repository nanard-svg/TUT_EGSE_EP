// Copyright 1986-2022 Xilinx, Inc. All Rights Reserved.
// --------------------------------------------------------------------------------
// Tool Version: Vivado v.2022.2 (win64) Build 3671981 Fri Oct 14 05:00:03 MDT 2022
// Date        : Wed Apr 24 07:55:56 2024
// Host        : DESKTOP-3HC2UMC running 64-bit major release  (build 9200)
// Command     : write_verilog -force -mode synth_stub
//               c:/3Utransat/TUT_EGSE_EP_checkout/Vivado/TUT_EGSE_EP.gen/sources_1/ip/fifo_pipe_in_w32_1024_r32_1024/fifo_pipe_in_w32_1024_r32_1024_stub.v
// Design      : fifo_pipe_in_w32_1024_r32_1024
// Purpose     : Stub declaration of top-level module interface
// Device      : xc7a75tfgg484-1
// --------------------------------------------------------------------------------

// This empty module with port declaration file causes synthesis tools to infer a black box for IP.
// The synthesis directives are for Synopsys Synplify support to prevent IO buffer insertion.
// Please paste the declaration into a Verilog source file or add the file as an additional source.
(* x_core_info = "fifo_generator_v13_2_7,Vivado 2022.2" *)
module fifo_pipe_in_w32_1024_r32_1024(rst, wr_clk, rd_clk, din, wr_en, rd_en, dout, full, 
  empty, valid, rd_data_count, wr_rst_busy, rd_rst_busy)
/* synthesis syn_black_box black_box_pad_pin="rst,wr_clk,rd_clk,din[31:0],wr_en,rd_en,dout[31:0],full,empty,valid,rd_data_count[9:0],wr_rst_busy,rd_rst_busy" */;
  input rst;
  input wr_clk;
  input rd_clk;
  input [31:0]din;
  input wr_en;
  input rd_en;
  output [31:0]dout;
  output full;
  output empty;
  output valid;
  output [9:0]rd_data_count;
  output wr_rst_busy;
  output rd_rst_busy;
endmodule
