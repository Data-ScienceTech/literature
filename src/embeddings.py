"""
Scientific text embeddings using SPECTER2 and sentence-transformers.
"""

import numpy as np
import pandas as pd
from sentence_transformers import SentenceTransformer
from typing import List, Union, Optional
import logging
import pathlib

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class ScientificEmbedder:
    """
    Wrapper for embedding scientific texts using pre-trained models.
    Default model is SPECTER2 for scientific papers.
    """
    
    def __init__(self, model_name: str = "allenai/specter2", device: Optional[str] = None):
        """
        Initialize the embedder.
        
        Parameters
        ----------
        model_name : str
            Name of the sentence-transformers model
        device : str, optional
            Device to use ('cuda', 'cpu', or None for auto-detection)
        """
        self.model_name = model_name
        logger.info(f"Loading embedding model: {model_name}")
        self.model = SentenceTransformer(model_name, device=device)
        logger.info(f"Model loaded successfully on device: {self.model.device}")
        
    def embed_texts(
        self, 
        texts: Union[List[str], pd.Series],
        batch_size: int = 32,
        show_progress: bool = True,
        normalize: bool = True
    ) -> np.ndarray:
        """
        Embed a list of texts into dense vectors.
        
        Parameters
        ----------
        texts : list or pd.Series
            List of text strings to embed
        batch_size : int
            Batch size for encoding
        show_progress : bool
            Show progress bar
        normalize : bool
            Normalize embeddings to unit length
            
        Returns
        -------
        np.ndarray
            Array of embeddings with shape (n_texts, embedding_dim)
        """
        # Convert to list if needed
        if isinstance(texts, pd.Series):
            texts = texts.tolist()
        
        # Filter out None/NaN values
        valid_texts = [str(t) if t is not None else "" for t in texts]
        
        logger.info(f"Embedding {len(valid_texts)} texts with batch_size={batch_size}")
        
        # Encode texts
        embeddings = self.model.encode(
            valid_texts,
            batch_size=batch_size,
            show_progress_bar=show_progress,
            convert_to_numpy=True,
            normalize_embeddings=normalize
        )
        
        logger.info(f"Generated embeddings with shape: {embeddings.shape}")
        
        return embeddings
    
    def save_embeddings(self, embeddings: np.ndarray, path: str):
        """Save embeddings to disk."""
        path = pathlib.Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        np.save(path, embeddings)
        logger.info(f"Saved embeddings to {path}")
    
    @staticmethod
    def load_embeddings(path: str) -> np.ndarray:
        """Load embeddings from disk."""
        embeddings = np.load(path)
        logger.info(f"Loaded embeddings with shape {embeddings.shape} from {path}")
        return embeddings


def embed_texts(
    texts: Union[List[str], pd.Series],
    model_name: str = "allenai/specter2",
    batch_size: int = 32,
    show_progress: bool = True,
    normalize: bool = True,
    device: Optional[str] = None
) -> np.ndarray:
    """
    Convenience function to embed texts using SPECTER2.
    
    Parameters
    ----------
    texts : list or pd.Series
        Texts to embed
    model_name : str
        Model name (default: SPECTER2)
    batch_size : int
        Batch size for encoding
    show_progress : bool
        Show progress bar
    normalize : bool
        Normalize embeddings to unit length
    device : str, optional
        Device to use
        
    Returns
    -------
    np.ndarray
        Embeddings array
    """
    embedder = ScientificEmbedder(model_name=model_name, device=device)
    return embedder.embed_texts(
        texts, 
        batch_size=batch_size,
        show_progress=show_progress,
        normalize=normalize
    )


def compute_similarity(emb1: np.ndarray, emb2: np.ndarray) -> float:
    """
    Compute cosine similarity between two embeddings.
    Assumes embeddings are already normalized.
    """
    return np.dot(emb1, emb2)


def find_similar_papers(
    query_idx: int,
    embeddings: np.ndarray,
    k: int = 10,
    exclude_self: bool = True
) -> np.ndarray:
    """
    Find k most similar papers to a query paper.
    
    Parameters
    ----------
    query_idx : int
        Index of query paper
    embeddings : np.ndarray
        All paper embeddings (normalized)
    k : int
        Number of similar papers to return
    exclude_self : bool
        Exclude the query paper itself from results
        
    Returns
    -------
    np.ndarray
        Indices of k most similar papers
    """
    # Compute similarities
    query_emb = embeddings[query_idx]
    similarities = embeddings @ query_emb
    
    # Get top k (k+1 if excluding self)
    top_k = k + 1 if exclude_self else k
    top_indices = np.argsort(similarities)[::-1][:top_k]
    
    # Remove self if needed
    if exclude_self:
        top_indices = top_indices[top_indices != query_idx][:k]
    
    return top_indices


if __name__ == "__main__":
    # Test the embedder
    test_texts = [
        "Machine learning models for predictive analytics in healthcare systems.",
        "Deep learning approaches for natural language processing and understanding.",
        "Organizational behavior and team dynamics in remote work environments.",
    ]
    
    logger.info("Testing embedder with sample texts...")
    embeddings = embed_texts(test_texts, batch_size=2)
    
    print(f"\nEmbedding shape: {embeddings.shape}")
    print(f"Embedding norms: {np.linalg.norm(embeddings, axis=1)}")
    
    # Test similarity
    sim_01 = compute_similarity(embeddings[0], embeddings[1])
    sim_02 = compute_similarity(embeddings[0], embeddings[2])
    print(f"\nSimilarity between text 0 and 1: {sim_01:.3f}")
    print(f"Similarity between text 0 and 2: {sim_02:.3f}")
