from functools import lru_cache

from sentence_transformers import SentenceTransformer, util
from tqdm import tqdm


class Model:

    def __init__(self, model_name):

        self._model = Model.get_model(model_name)

    @staticmethod
    @lru_cache(maxsize=None)
    def get_model(model_name):
        """
        Load and return a SentenceTransformer model with the given model name.
        Caches the model for future use to avoid reloading.
        """
        try:
            return SentenceTransformer(model_name)
        except Exception as e:
            raise SystemExit(
                f"Error occured while retrieving model - {model_name} : {e}"
            )

    def _similarity(self, sim_type="cosine"):
        if sim_type == "cosine":
            return util.cos_sim
        elif sim_type == "dot":
            return util.dot_score
        elif sim_type == "euclid":
            return util.euclidean_sim

    def get_embeddings(self, input):
        """Calculate and return embeddings"""
        for ele in tqdm(input, desc="Computing text embeddings"):
            embedding = self._model.encode(ele["text"])
            ele["embedding"] = embedding
        return input

    def query(self, query, embeddings, sim_type="cosine"):
        """
        Perform a semantic search over embeddings using the specified similarity metric.

        Encodes the query into an embedding and computes its similarity with each
        embedding in the list. Only embeddings with positive similarity scores are
        returned, sorted by similarity in descending order
        """

        query_embedding = self._model.encode(query)
        answers = []

        similarity = self._similarity(sim_type)

        for embedding in embeddings:
            score = similarity(query_embedding, embedding["embedding"]).item()

            # exclude negative similarities
            if score > 0:
                answers.append(
                    {
                        "content": {"text": embedding["text"]},
                        "type": "text",
                        "position": embedding["position"],
                        "similarity": score,
                        "id": embedding["id"],
                    }
                )

        return sorted(answers, key=lambda d: d["similarity"], reverse=True)
