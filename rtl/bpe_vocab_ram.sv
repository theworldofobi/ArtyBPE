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

  localparam int unsigned TABLE_A_BASE = 32'h0000_1000;
  localparam int unsigned TABLE_B_BASE = TABLE_A_BASE + (`BPE_TABLE_SIZE * 8);
  localparam int SLOT_BITS = `BPE_TABLE_A_BITS;

  (* ram_style = "block" *) logic [`BPE_ID_BITS-1:0]   base_mem [0:255];
  (* ram_style = "block" *) logic [`BPE_REC_BITS-1:0]  table_a  [0:`BPE_TABLE_SIZE-1];
  (* ram_style = "block" *) logic [``BPE_REC_BITS-1:0] table_b  [0:`BPE_TABLE_SIZE-1];

  initial begin
    $readmemh("/data/base_alphabet.mem", base_mem);
    $readmemh("/data/merge_table_a.mem", table_a);
    $readmemh("/data/merge_table_b.mem", table_b);
  end

  



endmodule
