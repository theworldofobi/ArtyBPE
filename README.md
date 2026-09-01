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
3. Need to format the JSON vocab into a trie transition table for my BRAM module. Important to make sure it can fit on the target device first which is 4.86 Mbits of memory. In order for it to fit and not consume the majority of resources I'm using a double-array trie structure (a la Darts/MeCab)