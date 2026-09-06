# ArtyBPE: Byte-Pair Encoding Engine in SystemVerilog for Arty A7-100T

People are often intrigued by my higher education trajectory as I received my bachelor's in Linguistics and Cognitive Science from UChicago and currently am pursuing a degree in Electrical and Computer Engineering at CU Boulder, as they are curious about the overlap. I figured it would be cute to put together a simple project that combines my computational linguistics background with my hardware description interests.

## Initial Setup

Verilator, cocotb, cocotbext-axi, tokenizers, and datasets, most installed with pip in venv

## General Process
1. Corpus extracted from Hugging Face dataset with short Python script: https://huggingface.co/datasets/KalsusEvening/financial-news-headlines

```
(venv) (base) obiuto@obiuto data ±|main ✗|→ python collect_data.py 
README.md: 100%|███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 7.34k/7.34k [00:00<00:00, 13.1MB/s]
train.csv: 100%|█████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████████| 943k/943k [00:00<00:00, 10.1MB/s]
Generating train split: 100%|██████████████████████████████████████████████████████████████████████████████████████████████████████| 10038/10038 [00:00<00:00, 672992.70 examples/s]
```

2. Train the BPE tokenizer on corpus
```
(venv) (base) obiuto@obiuto data ±|main ✗|→ python train_tokenizers.py 
[00:00:00] Pre-processing files (0 Mo)    ███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████                100%
[00:00:00] Tokenize words                 ███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████ 4151     /     4151
[00:00:00] Count pairs                    ███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████ 4151     /     4151
[00:00:00] Compute merges                 ███████████████████████████████████████████████████████████████████████████████████████████████████████████████████████ 3906     /     3906
```

3. Exporting the BPE tables for RTL

```
(venv) (base) obiuto@obiuto data ±|main✔|→ python export_bpe_tables.py 
vocab size:       3995 (id_bits=12)
base alphabet:    85 chars
merge rules:      3906 (rank_bits=12)
pair table:       16384 slots, 
24% full, max probe 8
verify_roundtrip: all 3906 entries verified

wrote base_alphabet.mem, merge_table.mem. bpe_params.svh
```

*Errors along the way*

"Never" is not iterable - trying to unpack each slot in the slot list while creating `merge_table.mem`, I figured because slots could be None, so I needed to make it an optional type
```python
# before
def place_with_linear_probing(pair_table, table_size):
  slots = [None] * table_size
  # rest of the function

# after
Slot = Optional[Tuple[int, int, int, int]]

def place_with_linear_probing(pair_table, table_size):
  slots: list[Slot] = [None] * table_size
  # rest of the function

# was causing error here
with open("merge_table.mem", "w") as f:
    for slot in slots:
      if slot is None:
        f.write("0" * hex_width + "\n")
      else:
        left, right, rank, merged_id = slot # HERE - "Never" is not iterable
```
