import numpy as np

from documents_app.models import chunk as Chunk
from .embedding import embed_query


def retrieve(query_text, user=None, k=5):
    qs = (
        Chunk.objects.exclude(embedding__isnull=True)
        .select_related('document')
    )
    if user is not None:
        qs = qs.filter(document__owner=user)

    chunks = list(qs.order_by('document_id', 'index'))

    if not chunks:
        return []

    vectors = np.array([c.embedding for c in chunks], dtype=np.float32)
    query_vec = np.array(embed_query(query_text), dtype=np.float32)

    scores = vectors @ query_vec

    top_indices = np.argsort(scores)[::-1][:k]

    results = []
    for i in top_indices:
        results.append({
            "chunk": chunks[i],
            "score": float(scores[i]),
        })

    return results