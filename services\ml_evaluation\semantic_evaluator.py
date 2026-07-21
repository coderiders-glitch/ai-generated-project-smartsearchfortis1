import os
import logging
from typing import List, Dict, Any
from dataclasses import dataclass
from datetime import datetime
import numpy as np
from sentence_transformers import SentenceTransformer, util

logger = logging.getLogger(__name__)


@dataclass
class EvaluationResult:
    """Represents a single semantic evaluation result."""
    query: str
    search_result: Dict[str, Any]
    ground_truth: Dict[str, Any]
    similarity_score: float
    is_relevant: bool
    evaluation_timestamp: datetime
    metadata: Dict[str, Any]


class SemanticEvaluator:
    """Evaluates semantic similarity between search results and ground truth data."""

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize the semantic evaluator with a pre-trained model.
        
        Args:
            model_name: Name of the sentence transformer model to use
        """
        self.model_name = model_name
        try:
            self.model = SentenceTransformer(model_name)
            logger.info(f"Loaded semantic model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to load model {model_name}: {e}")
            raise

    def encode_text(self, text: str) -> np.ndarray:
        """
        Encode text into semantic embeddings.
        
        Args:
            text: Text to encode
            
        Returns:
            Embedding vector as numpy array
        """
        try:
            embedding = self.model.encode(text, convert_to_tensor=False)
            return embedding
        except Exception as e:
            logger.error(f"Failed to encode text: {e}")
            raise

    def compute_similarity(self, embedding_a: np.ndarray, embedding_b: np.ndarray) -> float:
        """
        Compute cosine similarity between two embeddings.
        
        Args:
            embedding_a: First embedding vector
            embedding_b: Second embedding vector
            
        Returns:
            Similarity score between 0 and 1
        """
        try:
            similarity = float(util.pytorch_cos_sim(embedding_a, embedding_b)[0][0])
            return max(0.0, min(1.0, similarity))
        except Exception as e:
            logger.error(f"Failed to compute similarity: {e}")
            raise

    def evaluate_result(
        self,
        query: str,
        search_result: Dict[str, Any],
        ground_truth: Dict[str, Any],
        relevance_threshold: float = 0.7,
    ) -> EvaluationResult:
        """
        Evaluate semantic relevance of a search result against ground truth.
        
        Args:
            query: Original search query
            search_result: Search result from smart search service
            ground_truth: Ground truth data for comparison
            relevance_threshold: Threshold for marking result as relevant
            
        Returns:
            EvaluationResult containing similarity score and relevance judgment
        """
        try:
            result_text = self._extract_comparable_text(search_result)
            truth_text = self._extract_comparable_text(ground_truth)
            
            result_embedding = self.encode_text(result_text)
            truth_embedding = self.encode_text(truth_text)
            
            similarity_score = self.compute_similarity(result_embedding, truth_embedding)
            
            is_relevant = similarity_score >= relevance_threshold
            
            evaluation_result = EvaluationResult(
                query=query,
                search_result=search_result,
                ground_truth=ground_truth,
                similarity_score=similarity_score,
                is_relevant=is_relevant,
                evaluation_timestamp=datetime.utcnow(),
                metadata={
                    "model_name": self.model_name,
                    "relevance_threshold": relevance_threshold,
                }
            )
            
            logger.info(
                f"Evaluated query '{query}': similarity={similarity_score:.3f}, "
                f"relevant={is_relevant}"
            )
            return evaluation_result
        except Exception as e:
            logger.error(f"Failed to evaluate result: {e}")
            raise

    def batch_evaluate(
        self,
        queries: List[str],
        search_results: List[Dict[str, Any]],
        ground_truths: List[Dict[str, Any]],
        relevance_threshold: float = 0.7,
    ) -> List[EvaluationResult]:
        """
        Evaluate multiple search results in batch.
        
        Args:
            queries: List of search queries
            search_results: List of search results
            ground_truths: List of ground truth data
            relevance_threshold: Threshold for marking results as relevant
            
        Returns:
            List of EvaluationResult objects
        """
        if not (len(queries) == len(search_results) == len(ground_truths)):
            raise ValueError("Input lists must have equal length")
        
        results = []
        for query, search_result, ground_truth in zip(queries, search_results, ground_truths):
            try:
                result = self.evaluate_result(
                    query, search_result, ground_truth, relevance_threshold
                )
                results.append(result)
            except Exception as e:
                logger.error(f"Failed to evaluate batch item: {e}")
                continue
        
        logger.info(f"Batch evaluation complete: {len(results)}/{len(queries)} successful")
        return results

    def compute_metrics(
        self, evaluation_results: List[EvaluationResult]
    ) -> Dict[str, float]:
        """
        Compute aggregate metrics from evaluation results.
        
        Args:
            evaluation_results: List of evaluation results
            
        Returns:
            Dictionary containing precision, recall, f1, and mean similarity
        """
        if not evaluation_results:
            return {
                "precision": 0.0,
                "recall": 0.0,
                "f1_score": 0.0,
                "mean_similarity": 0.0,
                "total_evaluated": 0,
            }
        
        relevant_count = sum(1 for r in evaluation_results if r.is_relevant)
        total_count = len(evaluation_results)
        mean_similarity = np.mean([r.similarity_score for r in evaluation_results])
        
        precision = relevant_count / total_count if total_count > 0 else 0.0
        recall = precision
        f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0.0
        
        metrics = {
            "precision": float(precision),
            "recall": float(recall),
            "f1_score": float(f1_score),
            "mean_similarity": float(mean_similarity),
            "total_evaluated": total_count,
            "relevant_count": relevant_count,
        }
        
        logger.info(f"Computed metrics: {metrics}")
        return metrics

    @staticmethod
    def _extract_comparable_text(data: Dict[str, Any]) -> str:
        """
        Extract comparable text from search result or ground truth dictionary.
        
        Args:
            data: Dictionary containing search result or ground truth data
            
        Returns:
            Concatenated text for semantic comparison
        """
        text_fields = []
        for key in ["name", "title", "description", "specialty", "services"]:
            if key in data and data[key]:
                value = data[key]
                if isinstance(value, list):
                    text_fields.extend([str(v) for v in value])
                else:
                    text_fields.append(str(value))
        
        return " ".join(text_fields) if text_fields else ""