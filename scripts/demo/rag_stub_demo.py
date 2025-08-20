"""
RAG stub demo (concept only, no external deps).

- Uses a tiny in-memory corpus (id, text) and a simple bag-of-words vectorizer.
- Computes cosine similarity to retrieve top-k passages for a query.
- Assembles a prompt that includes retrieved context + the user question using your runtime builder.

Run examples:
  python scripts/demo/rag_stub_demo.py "How does BFS differ from DFS?"
  python scripts/demo/rag_stub_demo.py "Explain gradient descent" --top-k 3
"""
from __future__ import annotations
import argparse
from typing import List, Tuple
import math
from collections import Counter
from pathlib import Path
import importlib.util

# Load runtime builder
RUNTIME_BUILDER = Path(__file__).parents[2] / "backend" / "python_service" / "prompts" / "runtime_builder.py"
if not RUNTIME_BUILDER.exists():
    raise SystemExit("runtime_builder.py not found. Ensure repo structure is intact.")

spec = importlib.util.spec_from_file_location("runtime_builder", str(RUNTIME_BUILDER))
rb = importlib.util.module_from_spec(spec)  # type: ignore
spec.loader.exec_module(rb)  # type: ignore

# Tiny in-memory corpus
CORPUS: List[Tuple[str, str]] = [
    ("alg_bfs", "Breadth-first search explores neighbors level-by-level using a queue."),
    ("alg_dfs", "Depth-first search explores as far as possible along a branch using a stack or recursion."),
    ("ml_gd", "Gradient descent iteratively updates parameters in the direction of negative gradient to minimize loss."),
    ("ml_lr", "Logistic regression is a linear model for classification using the logistic (sigmoid) function."),
    ("sys_cache", "Caching stores results to serve repeated requests faster, trading memory for latency."),
]


def tokenize(text: str) -> List[str]:
    return [t.lower() for t in text.split()]


def vectorize(text: str) -> Counter:
    return Counter(tokenize(text))


def cosine_sim(a: Counter, b: Counter) -> float:
    # Compute cosine similarity between two sparse Counters
    if not a or not b:
        return 0.0
    common = set(a.keys()) & set(b.keys())
    dot = sum(a[t] * b[t] for t in common)
    na = math.sqrt(sum(v * v for v in a.values()))
    nb = math.sqrt(sum(v * v for v in b.values()))
    if na == 0 or nb == 0:
        return 0.0
    return dot / (na * nb)


def retrieve(query: str, top_k: int = 3) -> List[Tuple[str, str, float]]:
    qv = vectorize(query)
    scored = []
    for doc_id, text in CORPUS:
        score = cosine_sim(qv, vectorize(text))
        scored.append((doc_id, text, score))
    scored.sort(key=lambda x: x[2], reverse=True)
    return scored[:top_k]


def build_user_instruction(question: str, contexts: List[Tuple[str, str, float]]) -> str:
    # Construct a RAG-style instruction with context blocks
    lines = [
        "You are a helpful assistant. Use only the CONTEXT to answer the QUESTION.",
        "If the context is insufficient, say you don't know.",
        "\nCONTEXT:",
    ]
    for i, (doc_id, text, score) in enumerate(contexts, 1):
        lines.append(f"[{i}] id={doc_id} score={score:.3f}: {text}")
    lines.append("\nQUESTION:")
    lines.append(question)
    return "\n".join(lines)


def parse_args(argv: List[str]):
    p = argparse.ArgumentParser(description="RAG stub demo")
    p.add_argument("question", nargs="*", help="User question")
    p.add_argument("--top-k", type=int, default=3, help="Top-K retrieved passages")
    return p.parse_args(argv)


if __name__ == "__main__":
    args = parse_args(__import__('sys').argv[1:])
    question = " ".join(args.question) or "How does BFS differ from DFS?"

    hits = retrieve(question, top_k=args.top_k)
    instruction = build_user_instruction(question, hits)
    parts = rb.build_prompt(instruction)

    print("===== RAG STUB DEMO =====\n")
    print("----- SYSTEM -----\n")
    print(parts.system)
    print("\n----- USER (instruction with CONTEXT) -----\n")
    print(instruction)

    print("\nTop-K retrieved (id, score):")
    for doc_id, _text, score in hits:
        print(f"- {doc_id}: {score:.3f}")

    print("\nNote: Replace vectorize/retrieve with your embeddings + vector store in production.")