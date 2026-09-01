from datasets import load_dataset

data = load_dataset("KalsusEvening/financial-news-headlines")

with open("corpus.txt", "w", encoding="utf-8") as f:
  for i in range(5000):
    f.write(f"{data["train"][i]["headline"]}\n")
