`include "/data/bpe_params.svh"

module bpe_vocab_ram (
  input logic clk,
  input logic rst_n,

  input  logic                    base_request_valid,
  input  logic [7:0]              base_request_byte,
  output logic                    base_response_valid,
  output logic [`BPE_ID_BITS-1:0] base_response_id,

  input  logic                      pair_request_valid,
  input  logic [`BPE_ID_BITS-1:0]   pair_request_left,
  input  logic [`BPE_ID_BITS-1:0]   pair_request_right,
  output logic                      pair_response_valid,
  output logic                      pair_response_found,
  output logic [`BPE_RANK_BITS-1:0] pair_response_rank,
  output logic [`BPE_ID_BITS-1:0]   pair_response_merged_id,

  input  logic        s_axil_awvalid,
  output logic        s_axil_awready,
  input  logic [31:0] s_axil_awaddr,
  input  logic        s_axil_wrvalid,
  input  logic [31:0] s_axil_wdata,
  output logic        s_axil_bvalid,
  input  logic        s_axil_bready,
  output logic [1:0]  s_axil_bresponse
);


endmodule
