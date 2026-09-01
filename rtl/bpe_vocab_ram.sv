module bpe_vocab_ram (
  input logic clk
  // TODO: axi ports bla bla bla
);
  logic [31:0] bram [0:4096]; // dummy dimensions lowkey
  initial begin
    $readmemb("data/trie.mem", bram);
  end

  // TODO: sync read

endmodule
