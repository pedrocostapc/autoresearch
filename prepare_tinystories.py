"""
Materializa o dataset TinyStories como shards locais no formato que o
prepare.py espera — nenhuma mudança na lógica dele é necessária.

Baixa o parquet único de karpathy/tinystories-gpt4-clean e o divide em
N_TRAIN shards de treino (shard_00000..) + 1 shard de validação gravado com
o nome pinado VAL_FILENAME (shard_06542.parquet). Como o download do
prepare.py pula arquivos que já existem, rodar depois
`python prepare.py --num-shards <N_TRAIN>` não baixa nada do climbmix.

Uso (uma vez, antes do primeiro prepare.py):
    python prepare_tinystories.py
"""

import os

import pyarrow.parquet as pq
import requests

from prepare import DATA_DIR, VAL_FILENAME

URL = ("https://huggingface.co/datasets/karpathy/tinystories-gpt4-clean/"
       "resolve/main/tinystories_gpt4_clean.parquet")
N_TRAIN = 7  # shards de treino; val é o 8º pedaço


def main():
    os.makedirs(DATA_DIR, exist_ok=True)
    expected = [os.path.join(DATA_DIR, f"shard_{i:05d}.parquet") for i in range(N_TRAIN)]
    expected.append(os.path.join(DATA_DIR, VAL_FILENAME))
    if all(os.path.exists(p) for p in expected):
        print(f"TinyStories: {len(expected)} shards já existem em {DATA_DIR}")
        return

    src = os.path.join(DATA_DIR, "tinystories_gpt4_clean.parquet.src")
    if not os.path.exists(src):
        print("TinyStories: baixando parquet (~670MB)...")
        r = requests.get(URL, stream=True, timeout=60)
        r.raise_for_status()
        tmp = src + ".tmp"
        with open(tmp, "wb") as f:
            for chunk in r.iter_content(chunk_size=1024 * 1024):
                if chunk:
                    f.write(chunk)
        os.rename(tmp, src)

    table = pq.read_table(src)
    assert "text" in table.column_names, f"coluna 'text' ausente: {table.column_names}"
    n = table.num_rows
    pieces = N_TRAIN + 1
    step = n // pieces
    print(f"TinyStories: {n:,} docs -> {N_TRAIN} shards de treino + 1 val ({step:,} docs cada)")
    for i in range(pieces):
        start = i * step
        length = step if i < pieces - 1 else n - start
        piece = table.slice(start, length)
        name = VAL_FILENAME if i == pieces - 1 else f"shard_{i:05d}.parquet"
        out = os.path.join(DATA_DIR, name)
        pq.write_table(piece, out)
        print(f"  {name}: {piece.num_rows:,} docs")
    os.remove(src)
    print("TinyStories: pronto.")


if __name__ == "__main__":
    main()
