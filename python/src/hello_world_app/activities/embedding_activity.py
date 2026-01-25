"""
Activity for generating text embeddings using GPU-accelerated transformers.

This activity demonstrates using Python for GPU-intensive ML workloads
while .NET orchestrates the business logic via Dapr workflows.
"""
import logging
import time
from dataclasses import dataclass
from typing import List, Optional
from ..config import workflow_runtime

logger = logging.getLogger(__name__)

# Global model instance (lazy loaded)
_model = None
_model_name = "all-MiniLM-L6-v2"  # Fast, efficient sentence transformer


def _get_model():
    """Lazy load the sentence transformer model."""
    global _model
    if _model is None:
        try:
            from sentence_transformers import SentenceTransformer
            import torch

            logger.info(f"Loading sentence transformer model: {_model_name}")
            _model = SentenceTransformer(_model_name)

            # Select best available device
            if torch.backends.mps.is_available():
                device = "mps"  # Apple Silicon GPU (M1/M2/M3)
                logger.info("Model loaded on device: mps (Apple Silicon GPU)")
            elif torch.cuda.is_available():
                device = "cuda"  # NVIDIA GPU
                logger.info(f"Model loaded on device: cuda (NVIDIA GPU: {torch.cuda.get_device_name(0)})")
            else:
                device = "cpu"
                logger.info("Model loaded on device: cpu (no GPU available)")

            _model = _model.to(device)
        except ImportError as e:
            logger.error(f"Failed to import required libraries: {e}")
            raise RuntimeError(
                "sentence-transformers not installed. "
                "Install with: pip install sentence-transformers torch"
            )
    return _model


@dataclass
class EmbeddingRequest:
    """Request for text embedding generation."""
    texts: List[str]
    normalize: bool = True


@dataclass
class EmbeddingResponse:
    """Response containing embeddings and metadata."""
    embeddings: List[List[float]]
    model_name: str
    device: str
    dimension: int
    processing_time_ms: float
    num_texts: int


@workflow_runtime.activity(name='generate_embeddings')
def generate_embeddings(_ctx, input_data: dict) -> EmbeddingResponse:
    """
    Generate text embeddings using GPU-accelerated transformer models.

    Args:
        _ctx: Activity context
        input_data: Dictionary with 'texts' (list of strings) and optional 'normalize' (bool)

    Returns:
        EmbeddingResponse with embeddings and performance metrics
    """
    start_time = time.time()

    # Construct request from dict
    request = EmbeddingRequest(
        texts=input_data.get("texts", []),
        normalize=input_data.get("normalize", True)
    )

    if not request.texts:
        logger.warning("Empty text list provided")
        return EmbeddingResponse(
            embeddings=[],
            model_name=_model_name,
            device="none",
            dimension=0,
            processing_time_ms=0.0,
            num_texts=0
        )

    logger.info(f"Generating embeddings for {len(request.texts)} text(s)")

    try:
        import torch

        # Get model
        model = _get_model()

        # Determine which device is being used
        if torch.backends.mps.is_available():
            device = "mps"
        elif torch.cuda.is_available():
            device = "cuda"
        else:
            device = "cpu"

        # Generate embeddings
        embeddings = model.encode(
            request.texts,
            normalize_embeddings=request.normalize,
            convert_to_tensor=False  # Return as numpy arrays
        )

        # Convert to list of lists for JSON serialization
        embeddings_list = [emb.tolist() for emb in embeddings]

        processing_time = (time.time() - start_time) * 1000  # Convert to ms

        logger.info(
            f"Generated {len(embeddings_list)} embeddings "
            f"(dim={len(embeddings_list[0])}) in {processing_time:.2f}ms on {device}"
        )

        return EmbeddingResponse(
            embeddings=embeddings_list,
            model_name=_model_name,
            device=device,
            dimension=len(embeddings_list[0]) if embeddings_list else 0,
            processing_time_ms=processing_time,
            num_texts=len(request.texts)
        )

    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        raise


@workflow_runtime.activity(name='compute_similarity')
def compute_similarity(_ctx, input_data: dict) -> dict:
    """
    Compute cosine similarity between two sets of embeddings.

    Args:
        _ctx: Activity context
        input_data: Dictionary with 'embeddings1' and 'embeddings2' (lists of floats)

    Returns:
        Dictionary with similarity score
    """
    try:
        import numpy as np

        emb1 = np.array(input_data.get("embeddings1", []))
        emb2 = np.array(input_data.get("embeddings2", []))

        if emb1.size == 0 or emb2.size == 0:
            return {"similarity": 0.0, "error": "Empty embeddings provided"}

        # Compute cosine similarity
        similarity = float(np.dot(emb1, emb2) / (np.linalg.norm(emb1) * np.linalg.norm(emb2)))

        logger.info(f"Computed similarity: {similarity:.4f}")

        return {
            "similarity": similarity,
            "interpretation": _interpret_similarity(similarity)
        }

    except Exception as e:
        logger.error(f"Error computing similarity: {e}")
        return {"similarity": 0.0, "error": str(e)}


def _interpret_similarity(score: float) -> str:
    """Provide human-readable interpretation of similarity score."""
    if score >= 0.9:
        return "very_similar"
    elif score >= 0.7:
        return "similar"
    elif score >= 0.5:
        return "somewhat_similar"
    elif score >= 0.3:
        return "slightly_similar"
    else:
        return "dissimilar"
