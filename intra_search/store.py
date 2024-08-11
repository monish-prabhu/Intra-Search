import pickle
import os
import json

import platformdirs
import click

from .config import APP_NAME

"""
This module provides the `Store` class for managing document embeddings and metadata.

It handles saving, loading, and deleting embeddings with pickle, while maintaining 
a JSON manifest to track associated metadata.
"""


class Store:

    # os-specific path for caching embeddings
    dir_path = platformdirs.user_data_dir(APP_NAME)
    manifest_path = os.path.join(dir_path, "manifest.json")

    def __init__(self):

        # create directory to store document embeddings
        if not os.path.exists(self.dir_path):
            os.makedirs(self.dir_path)

        # create manifest file
        if not os.path.exists(self.manifest_path):
            with open(self.manifest_path, "w+") as f:
                json.dump([], f)

    def read_manifest(self):
        with open(self.manifest_path, "r") as f:
            return json.load(f)

    def get_meta(self, id):
        meta = list(filter(lambda x: x["id"] == id, self.read_manifest()))
        if len(meta) == 0:
            return None
        return meta[0]

    def _append_manifest(self, item):
        data = self.read_manifest()
        data.append(item)
        with open(self.manifest_path, "w") as f:
            json.dump(data, f, indent=4)

    def save(self, item, meta, file_name):
        pickle.dump(item, open(os.path.join(self.dir_path, file_name), "wb"))
        self._append_manifest(meta)

    def load(self, file_path):
        return pickle.load(open(file_path, "rb"))

    def exist(self, file_path, model_name, chunk_size):
        filter_func = lambda x: (
            x["document_path"] == file_path
            and x["chunk_size"] == chunk_size
            and x["model"] == model_name
        )
        return len(list(filter(filter_func, self.read_manifest()))) > 0

    def delete(self, files):
        meta = self.read_manifest()
        for file in files:

            file_path = os.path.abspath(file)
            file_name = os.path.basename(file)

            occurences = [x for x in meta if x["document_path"] == file_path]
            meta = [x for x in meta if x["document_path"] != file_path]

            if len(occurences) < 1:
                click.secho(f"No embeddings exists for {file_name} ({file_path}).")
                continue

            for ele in occurences:
                embedding_path = os.path.join(self.dir_path, ele["embedding_name"])
                if os.path.isfile(embedding_path):
                    os.remove(embedding_path)

            click.secho(
                f"Deleted all embeddings of {file_name}.",
                fg="green",
            )

        with open(self.manifest_path, "w") as f:
            json.dump(meta, f, indent=4)
