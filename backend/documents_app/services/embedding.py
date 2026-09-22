
from sentence_transformers import SentenceTransformer

from django.conf import settings

MODEL_DIR = settings.EMBEDDING_MODEL_PATH

_model = None


def get_model():
    global _model
    if _model is None:
        _model = SentenceTransformer(str(MODEL_DIR), device="cpu")
    return _model


def embed_passages(texts):
    model = get_model()
    prefixed = [f"passage: {t}" for t in texts]
    vectors = model.encode(
        prefixed,
        normalize_embeddings=True,
        batch_size=16,
    )
    return vectors.tolist()


def embed_query(text):
    model = get_model()
    vector = model.encode(
        f"query: {text}",
        normalize_embeddings=True,
    )
    return vector.tolist()