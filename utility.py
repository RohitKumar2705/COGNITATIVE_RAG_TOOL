"""
utility.py - Utility functions for array and embedding operations.
Provides helpers for numpy arrays, embeddings, and FAISS operations.
"""

import numpy as np
from typing import Tuple, List, Optional
import faiss


# ── Embedding Utilities ───────────────────────────────────────────────────────

def normalize_embedding(embedding: np.ndarray) -> np.ndarray:
    """
    Normalize embedding vector to unit length.
    
    Args:
        embedding: Embedding vector
    
    Returns:
        Normalized embedding
    """
    norm = np.linalg.norm(embedding)
    if norm == 0:
        return embedding
    return embedding / norm


def compute_cosine_similarity(vec1: np.ndarray, vec2: np.ndarray) -> float:
    """
    Compute cosine similarity between two vectors.
    
    Args:
        vec1: First vector
        vec2: Second vector
    
    Returns:
        Cosine similarity score (0-1)
    """
    vec1_norm = normalize_embedding(vec1)
    vec2_norm = normalize_embedding(vec2)
    return float(np.dot(vec1_norm, vec2_norm))


def batch_normalize_embeddings(embeddings: np.ndarray) -> np.ndarray:
    """
    Normalize a batch of embeddings.
    
    Args:
        embeddings: Array of embeddings (shape: N x D)
    
    Returns:
        Normalized embeddings
    """
    norms = np.linalg.norm(embeddings, axis=1, keepdims=True)
    norms[norms == 0] = 1  # Avoid division by zero
    return embeddings / norms


# ── FAISS Index Operations ────────────────────────────────────────────────────

def create_faiss_index(
    embeddings: np.ndarray,
    use_cosine: bool = True,
) -> faiss.IndexFlatIP:
    """
    Create a FAISS index from embeddings.
    
    Args:
        embeddings: Array of embeddings (shape: N x D)
        use_cosine: Whether to use cosine similarity (requires normalized embeddings)
    
    Returns:
        FAISS index
    """
    if embeddings.shape[0] == 0:
        raise ValueError("Cannot create index from empty embeddings")
    
    # Normalize if using cosine similarity
    if use_cosine:
        embeddings = batch_normalize_embeddings(embeddings.astype(np.float32))
    
    # Create index
    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim) if use_cosine else faiss.IndexFlatL2(dim)
    index.add(embeddings.astype(np.float32))
    
    return index


def search_faiss_index(
    index: faiss.IndexFlatIP,
    query_embedding: np.ndarray,
    k: int = 1,
    threshold: Optional[float] = None,
) -> Tuple[List[float], List[int]]:
    """
    Search FAISS index for nearest neighbors.
    
    Args:
        index: FAISS index
        query_embedding: Query embedding vector
        k: Number of results to return
        threshold: Optional similarity threshold
    
    Returns:
        Tuple of (scores, indices) for results above threshold
    """
    # Normalize query
    query = normalize_embedding(query_embedding).reshape(1, -1).astype(np.float32)
    
    # Search
    scores, indices = index.search(query, k)
    scores = scores[0]
    indices = indices[0]
    
    # Filter by threshold if specified
    if threshold is not None:
        mask = scores >= threshold
        scores = scores[mask]
        indices = indices[mask]
    
    return list(scores), list(indices)


# ── Array Operations ──────────────────────────────────────────────────────────

def stack_embeddings(embedding_list: List[np.ndarray]) -> np.ndarray:
    """
    Stack multiple embeddings into a matrix.
    
    Args:
        embedding_list: List of embedding vectors
    
    Returns:
        Matrix of embeddings (shape: N x D)
    """
    if not embedding_list:
        raise ValueError("Cannot stack empty list of embeddings")
    
    return np.vstack(embedding_list).astype(np.float32)


def get_embedding_dimension(embedding: np.ndarray) -> int:
    """Get dimension of an embedding."""
    return embedding.shape[0] if embedding.ndim == 1 else embedding.shape[1]


def ensure_embedding_shape(embedding: np.ndarray, expected_dim: Optional[int] = None) -> np.ndarray:
    """
    Ensure embedding has correct shape.
    
    Args:
        embedding: Embedding vector
        expected_dim: Expected dimension
    
    Returns:
        Embedding with correct shape
    """
    embedding = np.asarray(embedding).flatten().astype(np.float32)
    
    if expected_dim and len(embedding) != expected_dim:
        raise ValueError(
            f"Embedding dimension mismatch: got {len(embedding)}, "
            f"expected {expected_dim}"
        )
    
    return embedding


# ── Statistical Utilities ────────────────────────────────────────────────────

def compute_embedding_statistics(embeddings: np.ndarray) -> dict:
    """
    Compute statistics for a batch of embeddings.
    
    Args:
        embeddings: Array of embeddings (shape: N x D)
    
    Returns:
        Dictionary with statistics
    """
    if embeddings.shape[0] == 0:
        return {}
    
    return {
        'mean': float(np.mean(embeddings)),
        'std': float(np.std(embeddings)),
        'min': float(np.min(embeddings)),
        'max': float(np.max(embeddings)),
        'median': float(np.median(embeddings)),
        'num_vectors': int(embeddings.shape[0]),
        'dimension': int(embeddings.shape[1]) if embeddings.ndim > 1 else 1,
    }


def find_outlier_embeddings(
    embeddings: np.ndarray,
    threshold_std: float = 3.0,
) -> List[int]:
    """
    Find outlier embeddings based on mean distance.
    
    Args:
        embeddings: Array of embeddings
        threshold_std: Standard deviation threshold for outliers
    
    Returns:
        Indices of outlier embeddings
    """
    if embeddings.shape[0] < 2:
        return []
    
    # Compute mean embedding
    mean_embedding = np.mean(embeddings, axis=0)
    
    # Compute distances to mean
    distances = np.linalg.norm(embeddings - mean_embedding, axis=1)
    
    # Find outliers
    mean_dist = np.mean(distances)
    std_dist = np.std(distances)
    threshold = mean_dist + (threshold_std * std_dist)
    
    outlier_indices = np.where(distances > threshold)[0].tolist()
    
    return outlier_indices


# ── Batch Operations ──────────────────────────────────────────────────────────

def batch_compute_similarities(
    embeddings1: np.ndarray,
    embeddings2: np.ndarray,
) -> np.ndarray:
    """
    Compute pairwise similarities between two sets of embeddings.
    
    Args:
        embeddings1: First set of embeddings (shape: N x D)
        embeddings2: Second set of embeddings (shape: M x D)
    
    Returns:
        Similarity matrix (shape: N x M)
    """
    # Normalize both sets
    e1 = batch_normalize_embeddings(embeddings1)
    e2 = batch_normalize_embeddings(embeddings2)
    
    # Compute similarities
    similarities = np.dot(e1, e2.T)
    
    return similarities


def get_top_k_matches(
    similarities: np.ndarray,
    k: int = 5,
) -> List[Tuple[int, int, float]]:
    """
    Get top-k matches from similarity matrix.
    
    Args:
        similarities: Similarity matrix
        k: Number of top matches
    
    Returns:
        List of (row_idx, col_idx, similarity) tuples
    """
    matches = []
    
    for i in range(similarities.shape[0]):
        top_indices = np.argsort(similarities[i])[-k:][::-1]
        for j in top_indices:
            matches.append((i, int(j), float(similarities[i, j])))
    
    return sorted(matches, key=lambda x: x[2], reverse=True)
