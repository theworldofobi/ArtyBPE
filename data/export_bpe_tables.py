import json
import sys
import math
import random
from typing import Optional, Tuple

Entry = Tuple[int, int, int, int]
Slot = Optional[Tuple[int, int, int, int]]

TABLE_LOAD_FACTOR = 0.3
MAX_KICKS = 800
MAX_SEED_ATTEMPTS = 50
RANDOM_SEED = 0x9E3779B1

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

def make_hash(seed, table_size):
  mask = (1 << table_size.bit_length() - 1) - 1

  def h(left, right):
    x = (left * seed[0]) & 0xFFFFFFFF
    y = (right * seed[1]) & 0xFFFFFFFF
    return (x ^ y ^ seed[2]) & mask

  return h


def build_cuckoo_tables(pair_table, table_size, rng):
  for attempt in range(MAX_SEED_ATTEMPTS):
    seed_a = (rng.getrandbits(32) | 1, rng.getrandbits(32) | 1, rng.getrandbits(32))
    seed_b = (rng.getrandbits(32) | 1, rng.getrandbits(32) | 1, rng.getrandbits(32))

    h_a = make_hash(seed_a, table_size)
    h_b = make_hash(seed_b, table_size)

    table_a : list[Slot] = [None] * table_size
    table_b : list[Slot] = [None] * table_size
    ok = True

    for (left, right), (rank, merged_id) in pair_table.items():
      curr : Entry = (left, right, rank, merged_id)
      in_table_a = True
      placed = False
      for _ in range(MAX_KICKS):
        table, h = (table_a, h_a) if in_table_a else (table_b, h_b)
        addr = h(curr[0], curr[1])

        if table[addr] is None:
          table[addr] = curr
          placed = True
          break
        occupant = table[addr]
        table[addr] = curr
        curr = occupant
        in_table_a = not in_table_a

      if not placed:
        ok = False
        break

    if ok:
      return table_a, table_b, seed_a, seed_b, attempt

  sys.exit(f"build_cuckoo_tables: cuckoo placement failed after {MAX_SEED_ATTEMPTS}, raise total load factor")

def verify_roundtrip(pair_table, table_a, table_b, seed_a, seed_b, table_size):
  h_a = make_hash(seed_a, table_size)
  h_b = make_hash(seed_b, table_size)
  for (left, right), (rank, merged_id) in pair_table.items():
    slot_a = table_a[h_a(left, right)]
    slot_b = table_b[h_b(left, right)]

    match_a = slot_a is not None and slot_a[:2] == (left, right)
    match_b = slot_b is not None and slot_b[:2] == (left, right)

    if not (match_a or match_b):
      sys.exit(f"verify_roundtrip: could not find ({left},{right}) pair in either table")

    found = slot_a if match_a else slot_b
    if found is not None and found[2:] != (rank, merged_id):
      sys.exit(f"verify_roundtrip: rank/merged_id mismatch for ({left},{right}) pair")

  print(f"verify_roundtrip: all {len(pair_table)} entries verified")

def pack_record(slot, rec_bits, id_bits, rank_bits):
  if slot is None:
    return 0

  left, right, rank, merged_id = slot
  word = (1 << (rec_bits - 1))
  word |= left << (2 * id_bits + rank_bits)
  word |= right << (id_bits + rank_bits)
  word |= rank << id_bits
  word |= merged_id

  return word

if __name__ == "__main__":
  vocab, merges = load_bpe_model("vocab.json")
  unk_id = vocab.get("[UNK]", 0)
  base_chars = {t: i for t, i in vocab.items() if len(t) == 1}
  pair_table = build_pair_table(vocab, merges)

  vocab_size = len(vocab)
  num_merges = len(merges)
  id_bits = max(1, math.ceil(math.log2(vocab_size)))
  rank_bits = max(1, math.ceil(math.log2(max(num_merges, 2))))

  table_size = 1
  while table_size < num_merges / (2 * TABLE_LOAD_FACTOR):
    table_size *= 2

  rng = random.Random(RANDOM_SEED)
  table_a, table_b, seed_a, seed_b, attempt = build_cuckoo_tables(pair_table, table_size, rng)

  print(f"vocab size:       {vocab_size} (id_bits={id_bits})")
  print(f"base alphabet:    {len(base_chars)} chars")
  print(f"merge rules:      {num_merges} (rank_bits={rank_bits})")

  fill_a = sum(1 for slot in table_a if slot is not None)
  fill_b = sum(1 for slot in table_b if slot is not None)
  print(f"pair table:       {table_size} slots")
  print(f"table_a: {fill_a / table_size:.0%} full, table_b: {fill_b / table_size:.0%} full,")
  print(f"placed on seed attempt {attempt}")

  verify_roundtrip(pair_table, table_a, table_b, seed_a, seed_b, table_size)

  # base_alphabet.mem
  with open("base_alphabet.mem", "w") as f:
    for byte_val in range(256):
      tid = base_chars.get(chr(byte_val), unk_id)
      f.write(f"t{tid:0{(id_bits + 3) // 4}X}\n")

  # merge_table_a.mem and merge_table_b.mem
  rec_bits = 1 + 2 * id_bits + rank_bits + id_bits
  hex_width = (rec_bits + 3) // 4

  for name, table in [("merge_table_a.mem", table_a), ("merge_table_b.mem", table_b)]:
    with open(name, "w") as f:
      for slot in table:
        word = pack_record(slot, rec_bits, id_bits, rank_bits)
        f.write(f"{word:0{hex_width}X}\n")
      
  # bpe_params.svh
  with open("bpe_params.svh", "w") as f:
    f.write(f"`define BPE_ID_BITS       {id_bits}\n")
    f.write(f"`define BPE_RANK_BITS     {rank_bits}\n")
    f.write(f"`define BPE_REC_BITS      {rec_bits}\n")
    f.write(f"`define BPE_TABLE_SIZE    {table_size}\n")
    f.write(f"`define BPE_VOCAB_SIZE    {vocab_size}\n")
    f.write(f"`define BPE_NUM_MERGES    {num_merges}\n")
    f.write(f"`define BPE_UNK_ID        {unk_id}\n")
    f.write(f"`define BPE_SEED_A0       32'h{seed_a[0]:08X}\n")
    f.write(f"`define BPE_SEED_A1       32'h{seed_a[1]:08X}\n")
    f.write(f"`define BPE_SEED_A2       32'h{seed_a[2]:08X}\n")
    f.write(f"`define BPE_SEED_B0       32'h{seed_b[0]:08X}\n")
    f.write(f"`define BPE_SEED_B1       32'h{seed_b[1]:08X}\n")
    f.write(f"`define BPE_SEED_B2       32'h{seed_b[2]:08X}\n")

  print("\nwrote base_alphabet.mem, merge_table_a.mem, merge_table_b.mem, and bpe_params.svh")
