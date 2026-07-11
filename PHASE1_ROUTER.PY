"""
Phase 1: Vector-Based Persona Matching (The Router)
Uses Google Generative AI embeddings + FAISS for cosine similarity routing.
"""

import os
import numpy as np
import faiss
from dotenv import load_dotenv
import google.generativeai as genai

load_dotenv()

# Configure Google Generative AI
genai.configure(api_key=os.environ.get("GOOGLE_API_KEY"))

# ── Bot Personas ──────────────────────────────────────────────────────────────
BOT_PERSONAS = {
    "bot_a": {
        "name": "Tech Maximalist",
        "description": (
            "I believe AI and crypto will solve all human problems. "
            "I am highly optimistic about technology, Elon Musk, and space exploration. "
            "I dismiss regulatory concerns."
        ),
    },
    "bot_b": {
        "name": "Doomer / Skeptic",
        "description": (
            "I believe late-stage capitalism and tech monopolies are destroying society. "
            "I am highly critical of AI, social media, and billionaires. "
            "I value privacy and nature."
        ),
    },
    "bot_c": {
        "name": "Finance Bro",
        "description": (
            "I strictly care about markets, interest rates, trading algorithms, "
            "and making money. I speak in finance jargon and view everything "
            "through the lens of ROI."
        ),
    },
}


def get_embedding(text: str) -> np.ndarray:
    """Get embedding vector from Google Generative AI."""
    result = genai.embed_content(
        model="models/embedding-001",
        content=text,
        task_type="SEMANTIC_SIMILARITY",
    )
    return np.array(result["embedding"], dtype=np.float32)


def build_persona_index() -> tuple[faiss.IndexFlatIP, list[str]]:
    """
    Build a FAISS index from bot persona embeddings.
    Returns the index and an ordered list of bot IDs.
    """
    bot_ids = list(BOT_PERSONAS.keys())
    embeddings = []

    print("📦 Building persona vector index...")
    for bot_id in bot_ids:
        persona_text = BOT_PERSONAS[bot_id]["description"]
        emb = get_embedding(persona_text)
        # Normalize for cosine similarity via inner product
        emb = emb / np.linalg.norm(emb)
        embeddings.append(emb)
        print(f"  ✅ Embedded {bot_id} ({BOT_PERSONAS[bot_id]['name']})")

    matrix = np.vstack(embeddings)
    dim = matrix.shape[1]

    # IndexFlatIP computes inner product → cosine similarity (on normalized vecs)
    index = faiss.IndexFlatIP(dim)
    index.add(matrix)
    print(f"  🗄️  FAISS index built: {index.ntotal} vectors, dim={dim}\n")
    return index, bot_ids


def route_post_to_bots(
    post_content: str,
    threshold: float = 0.55,  # Gemini embeddings; tune as needed
    index: faiss.IndexFlatIP = None,
    bot_ids: list[str] = None,
) -> list[dict]:
    """
    Embed the post and return bots whose persona similarity exceeds threshold.

    Args:
        post_content: The incoming social-media post text.
        threshold:    Cosine-similarity cutoff (0-1). Default 0.55 works well
                      with embedding-001 embeddings; raise/lower as needed.
        index:        Pre-built FAISS index (built once at startup).
        bot_ids:      Ordered list of bot IDs matching the index rows.

    Returns:
        List of dicts: [{"bot_id": ..., "name": ..., "similarity": ...}]
    """
    post_emb = get_embedding(post_content)
    post_emb = post_emb / np.linalg.norm(post_emb)
    query = post_emb.reshape(1, -1)

    scores, indices = index.search(query, k=len(bot_ids))

    matched = []
    for score, idx in zip(scores[0], indices[0]):
        if score >= threshold:
            bot_id = bot_ids[idx]
            matched.append(
                {
                    "bot_id": bot_id,
                    "name": BOT_PERSONAS[bot_id]["name"],
                    "similarity": float(score),
                }
            )

    return matched


# ── Demo ──────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    index, bot_ids = build_persona_index()

    test_posts = [
        "OpenAI just released a new model that might replace junior developers.",
        "Bitcoin hits new all-time high as ETFs flood the market with capital.",
        "Big Tech is lobbying governments to weaken privacy laws for profit.",
    ]

    print("=" * 60)
    print("🔀  PHASE 1 — POST ROUTING RESULTS")
    print("=" * 60)

    for post in test_posts:
        print(f"\n📨 Post: \"{post}\"")
        matches = route_post_to_bots(post, threshold=0.55, index=index, bot_ids=bot_ids)
        if matches:
            for m in matches:
                print(f"  → {m['bot_id']} ({m['name']})  similarity={m['similarity']:.4f}")
        else:
            print("  → No bots matched above threshold.")
