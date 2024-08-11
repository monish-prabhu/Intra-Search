import os

from flask import Flask, request, send_file, jsonify, send_from_directory
from flask_cors import CORS

from .store import Store
from .model import Model
from .config import STATIC_FOLDER

app = Flask(__name__, static_folder=STATIC_FOLDER)
cors = CORS(app)
store = Store()
_cache = {}


@app.route("/")
def index():
    """Route to serve index.html (entry point)"""
    return send_from_directory(app.static_folder, "index.html")


@app.route("/<path:path>")
def static_proxy(path):
    """Route to serve static assets"""
    return send_from_directory(app.static_folder, path)


@app.route("/api/embeddings")
def get_embeddings_info():
    """GET - all embeddings info from manifest.json"""
    try:
        return store.read_manifest()
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/doc/<embedding_id>")
def send_doc(embedding_id):
    """GET - serve original document"""
    try:
        embedding_meta = store.get_meta(embedding_id)

        if embedding_meta is None:
            return "Unable to find document embeddings", 404

        document_path = embedding_meta["document_path"]

        return send_file(
            document_path,
            mimetype="application/pdf",
        )
    except FileNotFoundError:
        return "Document not found", 404
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/api/<embedding_id>/query")
def query_doc(embedding_id):
    """GET - query document embedding"""
    try:
        embedding = None
        query_string = request.args["query"]

        if embedding_id in _cache:
            embedding = _cache[embedding_id]
        else:
            embedding_meta = store.get_meta(embedding_id)
            if embedding_meta is None:
                return "Unable to find document embeddings", 404

            embedding = store.load(
                os.path.join(store.dir_path, embedding_meta["embedding_name"])
            )

            # Cache the loaded embeddings in-memory
            _cache[embedding_id] = embedding

        model = Model(
            model_name=embedding["model"],
        )

        return model.query(query=query_string, embeddings=embedding["embeddings"])

    except Exception as e:
        return jsonify({"error": str(e)}), 500
