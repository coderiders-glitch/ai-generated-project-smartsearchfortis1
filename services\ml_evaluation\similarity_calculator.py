import logging
from typing import List, Dict, Any, Tuple
import numpy as np
from sentence_transformers import util

logger = logging.getLogger(__name__)


class SimilarityCalculator:
    """Calculates various similarity metrics between embeddings and text."""

    @staticmethod
    def cosine_similarity(embedding_a: np.ndarray, embedding_b: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding_a: First embedding vector
            embedding_b: Second embedding vector
            
        Returns:
            Cosine similarity score between -1 and 1
        """
        try:
            similarity = float(util.pytorch_cos_sim(embedding_a, embedding_b)[0][0])
            return similarity
        except Exception as e:
            logger.error(f"Failed to calculate cosine similarity: {e}")
            raise

    @staticmethod
    def euclidean_distance(embedding_a: np.ndarray, embedding_b: np.ndarray) -> float:
        """
        Calculate Euclidean distance between two embeddings.
        
        Args:
            embedding_a: First embedding vector
            embedding_b: Second embedding vector
            
        Returns:
            Euclidean distance
        """
        try:
            distance = float(np.linalg.norm(embedding_a - embedding_b))
            return distance
        except Exception as e:
            logger.error(f"Failed to calculate Euclidean distance: {e}")
            raise

    @staticmethod
    def manhattan_distance(embedding_a: np.ndarray, embedding_b: np.ndarray) -> float:
        """
        Calculate Manhattan distance between two embeddings.
        
        Args:
            embedding_a: First embedding vector
            embedding_b: Second embedding vector
            
        Returns:
            Manhattan distance
        """
        try:
            distance = float(np.sum(np.abs(embedding_a - embedding_b)))
            return distance
        except Exception as e:
            logger.error(f"Failed to calculate Manhattan distance: {e}")
            raise

    @staticmethod
    def batch_similarity(
        embeddings_a: List[np.ndarray],
        embeddings_b: List[np.ndarray],
        metric: str = "cosine",
    ) -> List[float]:
        """
        Calculate similarity between multiple embedding pairs.
        
        Args:
            embeddings_a: List of first embeddings
            embeddings_b: List of second embeddings
            metric: Similarity metric ('cosine', 'euclidean', 'manhattan')
            
        Returns:
            List of similarity scores
        """
        if len(embeddings_a) != len(embeddings_b):
            raise ValueError("Embedding lists must have equal length")
        
        try:
            similarities = []
            for emb_a, emb_b in zip(embeddings_a, embeddings_b):
                if metric == "cosine":
                    sim = SimilarityCalculator.cosine_similarity(emb_a, emb_b)
                elif metric == "euclidean":
                    sim = SimilarityCalculator.euclidean_distance(emb_a, emb_b)
                elif metric == "manhattan":
                    sim = SimilarityCalculator.manhattan_distance(emb_a, emb_b)
                else:
                    raise ValueError(f"Unknown metric: {metric}")
                similarities.append(sim)
            
            logger.info(f"Calculated {len(similarities)} similarities using {metric} metric")
            return similarities
        except Exception as e:
            logger.error(f"Failed to calculate batch similarities: {e}")
            raise

    @staticmethod
    def rank_by_similarity(
        query_embedding: np.ndarray,
        candidate_embeddings: List[np.ndarray],
        candidates: List[Dict[str, Any]],
        top_k: int = 10,
    ) -> List[Tuple[Dict[str, Any], float]]:
        """
        Rank candidates by similarity to query embedding.
        
        Args:
            query_embedding: Query embedding vector
            candidate_embeddings: List of candidate embeddings
            candidates: List of candidate data objects
            top_k: Number of top results to return
            
        Returns:
            List of tuples (candidate, similarity_score) sorted by similarity
        """
        if len(candidate_embeddings) != len(candidates):
            raise ValueError("Embeddings and candidates lists must have equal length")
        
        try:
            similarities = []
            for candidate, candidate_embedding in zip(candidates, candidate_embeddings):
                sim = SimilarityCalculator.cosine_similarity(query_embedding, candidate_embedding)
                similarities.append((candidate, sim))
            
            ranked = sorted(similarities, key=lambda x: x[1], reverse=True)
            result = ranked[:top_k]
            
            logger.info(f"Ranked {len(candidates)} candidates, returning top {len(result)}")
            return result
        except Exception as e:
            logger.error(f"Failed to rank candidates by similarity: {e}")
            raise

    @staticmethod
    def compute_similarity_matrix(
        embeddings: List[np.ndarray],
    ) -> np.ndarray:
        """
        Compute pairwise similarity matrix for a list of embeddings.
        
        Args:
            embeddings: List of embedding vectors
            
        Returns:
            Similarity matrix as numpy array
        """
        try:
            embeddings_array = np.array(embeddings)
            similarity_matrix = util.pytorch_cos_sim(embeddings_array, embeddings_array)
            return similarity_matrix.numpy()
        except Exception as e:
            logger.error(f"Failed to compute similarity matrix: {e}")
            raise