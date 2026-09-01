from tokenizers import Tokenizer, models, trainers, pre_tokenizers

tokenizer = Tokenizer(models.BPE(unk_token="[UNK]"))
tokenizer.pre_tokenizer = pre_tokenizers.Whitespace()

trainer = trainers.BpeTrainer(
  vocab_size=4096,
  min_frequency=2,
  special_tokens=["[UNK]", "[PAD]", "[BOS]", "[EOS]"]
)
# UNK is for unknown, PAD for padding, BOS for beginning of sequence, EOS for end of sequence

tokenizer.train(files=["corpus.txt"], trainer=trainer)
tokenizer.save("vocab.json")
