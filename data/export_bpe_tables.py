import json
import sys
import math
from typing import Optional, Tuple

Slot = Optional[Tuple[int, int, int, int]]

TABLE_LOAD_FACTOR = 0.4

def load_bpe_model(path):
  with open(path, "r", encoding="utf-8") as f:
    token = json.load(f)

  model = token["model"]
  vocab = model["vocab"]

  raw_merges = model["merges"]
  merges = []
  for m in raw_merges:
    if isinstance(m, str):
      left, right = m.split(" ")
    else:
      left, right = m[0], m[1]
    merges.append((left, right))

  return vocab, merges

def build_pair_table(vocab, merges):
  pair_table = {}
  skipped = 0

  for rank, (left, right) in enumerate(merges):
    merged = left + right
    if left not in vocab or right not in vocab or merged not in vocab:
      skipped += 1
      continue
    pair_table[(vocab[left], vocab[right])] = (rank, vocab[merged])
  if skipped:
    print(f"skipped {skipped} merges that referenced a token missing from vocab", file=sys.stderr)

  return pair_table

# knuth
def hash_pair(left, right, size):
  return ((left * 2654435761) ^ (right * 40503761)) & (size - 1)

def place_with_linear_probing(pair_table, table_size):
  slots: list[Slot] = [None] * table_size
  max_probe = 0

  for (left, right), (rank, merged_id) in pair_table.items():
    addr = hash_pair(left, right, table_size)
    probe = 0

    while slots[addr] is not None:
      addr = (addr + 1) % table_size
      probe += 1
      if probe >= table_size:
        sys.exit("merge_table is full, increase table size")

    slots[addr] = (left, right, rank, merged_id)
    max_probe = max(max_probe, probe)

  return slots, max_probe

def verify_roundtrip(pair_table, slots, table_size):
  for (left, right), (rank, merged_id) in pair_table.items():
    addr = hash_pair(left, right, table_size)
    probe = 0
    found = False

    while probe < table_size:
      slot = slots[addr]

      if slot is None:
        break
      if slot[0] == left and slot[1] == right:
        found = True
        break

      addr = (addr + 1) % table_size
      probe += 1

    if not found or slots[addr][2:] != (rank, merged_id):
      sys.exit(f"roundtrip check failed for pair ({left}, {right})")

  print(f"verify_roundtrip: all {len(pair_table)} entries verified")

if __name__ == "__main__":
  vocab, merges = load_bpe_model("vocab.json")
  unk_id = vocab.get("[UNK]", 0)
  base_chars = {t: i for t, i in vocab.items if len(t) == 1}
  pair_table = build_pair_table(vocab, merges)

  vocab_size = len(vocab)
  num_merges = len(merges)
  id_bits = max(1, math.ceil(math.log2(vocab_size)))
  rank_bits = max(1, math.ceil(math.log2(max(num_merges, 2))))

  table_size = 1
  while table_size < num_merges / TABLE_LOAD_FACTOR:
    table_size *= 2
  slots, max_probe = place_with_linear_probing(pair_table, table_size)

  print(f"vocab size:       {vocab_size} (id_bits={id_bits})")
  print(f"base alphabet:    {len(base_chars)} chars")
  print(f"merge rules:      {num_merges} (rank_bits={rank_bits})")
  print(f"pair table:       {table_size} slots, ")
  print(f"{len(pair_table) / table_size:.0%} full, max probe {max_probe}")

  verify_roundtrip(pair_table, slots, table_size)

  # base_alphabet.mem
  with open("base_alphabet.mem", "w") as f:
    for byte_val in range(256):
      tid = base_chars.get(chr(byte_val), unk_id)
      f.write(f"t{tid:0{(id_bits + 3) // 4}X}\n")

  # merge_table.mem
  rec_bits = 1 + 3 * id_bits + rank_bits
  hex_width = (rec_bits + 3) // 4

  with open("merge_table.mem", "w") as f:
    for slot in slots:
      if slot is None:
        f.write("0" * hex_width + "\n")
      else:
        left, right, rank, merged_id = slot
        word = (1 << (rec_bits - 1))
        word |= left << (2 * id_bits + rank_bits)
        word |= right << (id_bits + rank_bits)
        word |= rank << id_bits
        word |= merged_id
        f.write(f"{word:0{hex_width}X}\n")
        
  # bpe_params.mem
  with open("bpe_params.svh", "w") as f:
    f.write(f"`define BPE_ID_BITS       {id_bits}\n")
    f.write(f"`define BPE_RANK_BITS     {rank_bits}\n")
    f.write(f"`define BPE_REC_BITS      {rec_bits}\n")
    f.write(f"`define BPE_TABLE_SIZE    {table_size}\n")
    f.write(f"`define BPE_VOCAB_SIZE    {vocab_size}\n")
    f.write(f"`define BPE_NUM_MERGES    {num_merges}\n")
    f.write(f"`define BPE_UNK_ID        {unk_id}\n")

  print("\nwrote base_alphabet.mem, merge_table.mem. bpe_params.svh")
