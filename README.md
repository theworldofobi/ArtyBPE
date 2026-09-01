# ArtyBPE: Byte-Pair Encoding Engine in SystemVerilog for Arty A7-100T

People are often intrigued by my higher education trajectory as I received my bachelor's in Linguistics and Cognitive Science from UChicago and currently am pursuing a degree in Electrical and Computer Engineering at CU Boulder, as they are curious by the overlap. I figured it would be cute to put together a simple project that combines my computational linguistics background with my hardware description interests.

## Initial Setup

Verilator, cocotb, cocotbext-axi, tokenizers, and datasets, most installed with pip in venv

## General Process
1. Corpus extracted from Hugging Face dataset with short Python script: https://huggingface.co/datasets/KalsusEvening/financial-news-headlines
2. Train the BPE tokenizer on corpus
3. 