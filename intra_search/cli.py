"""
This module defines the following CLI commands:
- `create`: Generate document embeddings using specified model and chunk size.
- `start`: Launch the Flask server to serve the API and web application.
- `remove`: Delete existing embeddings based on specified document files.
- `list`: Display a list of all cached embeddings.
"""

import os
from uuid import uuid4

import click

from .server import app
from .doc import Pdf
from .model import Model
from .store import Store
from .utils import sanitize_filename
from .config import DEFAULT_MODEL, DEFAULT_CHUNK_SIZE, DEFAULT_PORT, HOST, SHORT_DESC


@click.group(invoke_without_command=True, help=SHORT_DESC)
@click.pass_context
@click.option(
    "--show-dir",
    "-d",
    "show_dir",
    is_flag=True,
    help="Show the directory where document embeddings are stored.",
)
def cli(ctx, show_dir):
    if ctx.invoked_subcommand is None:
        if show_dir:
            print(Store.dir_path)
            ctx.exit()
    else:
        pass


@click.command()
@click.argument(
    "files",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        path_type=str,
    ),
    nargs=-1,
    required=True,
)
@click.option(
    "--model",
    "-m",
    "model_name",
    default=DEFAULT_MODEL,
    show_default=True,
    help="Embedding model",
)
@click.option(
    "--chunks",
    "-n",
    "chunk_size",
    default=DEFAULT_CHUNK_SIZE,
    show_default=True,
    type=click.IntRange(10, None),
    help="Chunk size, must be greater than 10",
)
def create(files, model_name, chunk_size):
    """Create document embeddings"""
    try:
        completed = []
        store = Store()
        for file in files:

            doc = Pdf(file)

            """ Skip file if embeddings already exists """
            if store.exist(
                file_path=doc.file_path,
                model_name=model_name,
                chunk_size=chunk_size,
            ):
                click.secho(
                    f"Embedding already exists for document - {doc.file_name}",
                    fg="green",
                )
                continue

            model = Model(model_name=model_name)

            click.secho(f"Processing document: {doc.file_name}", bg="blue", fg="white")

            embedding_file_name = (
                sanitize_filename(
                    "_".join(map(str, [doc.file_name, model_name, chunk_size]))
                )
                + ".pkl"
            )

            emeddings_meta = {
                "id": str(uuid4()),
                "model": model_name,
                "chunk_size": chunk_size,
                "document_path": doc.file_path,
                "document_name": doc.file_name,
                "embedding_name": embedding_file_name,
            }

            store.save(
                file_name=embedding_file_name,
                meta=emeddings_meta,
                item={
                    **emeddings_meta,
                    "embeddings": model.get_embeddings(
                        doc.extract_text(chunk_size=chunk_size)
                    ),
                },
            )

            completed.append(doc.file_name)

        cmpl_message = "Embeddings created for the documents:\n"
        cmpl_message += "\n".join(completed)
        click.secho(
            cmpl_message,
            fg="green",
        )
        click.secho(
            "\nRun 'intra-search start' to start the server.\n",
            fg="green",
            bold=True,
        )

    except Exception as e:
        click.secho(f"{e}", err=True)


@click.command()
@click.option(
    "--port",
    "-p",
    default=DEFAULT_PORT,
    show_default=True,
    type=click.INT,
    help="Port of the Flask app (By default, the Flask app runs on port=5000)",
)
def start(port):
    """Start the flask application (which serves both API and web app)"""
    try:
        app.run(host=HOST, port=port)
    except Exception as e:
        click.echo(f"{e}", err=True)
        click.echo(
            f"Try launching the server on a different port by passing --port/-p PORT ",
            bold=True,
        )


@click.command()
@click.argument(
    "files",
    type=click.Path(
        exists=True,
        file_okay=True,
        dir_okay=False,
        readable=True,
        path_type=str,
    ),
    nargs=-1,
    required=True,
)
def remove(files):
    """Remove embeddings"""
    try:
        store = Store()
        cnf_message = "\nThis action will delete all embeddings created using the following documents:\n\n"
        cnf_message += "\n".join(
            [f"{os.path.basename(file)} ({os.path.abspath(file)})" for file in files]
        )
        click.secho(
            cnf_message,
            fg="red",
            bold=True,
        )

        if click.confirm("\n\n Proceed?", default=False, abort=True):
            store.delete(files)

    except Exception as e:
        click.echo(f"{e}", err=True)


@click.command()
def list():
    """List all cached embeddings"""
    try:
        from tabulate import tabulate

        store = Store()
        meta = store.read_manifest()
        header = ["document", "model", "chunk size"]
        rows = [
            [
                ele["document_name"],
                ele["model"],
                ele["chunk_size"],
            ]
            for ele in meta
        ]
        click.echo(tabulate(rows, header))

    except Exception as e:
        click.echo(f"{e}", err=True)


cli.add_command(create)
cli.add_command(start)
cli.add_command(remove)
cli.add_command(list)

if __name__ == "__main__":
    cli()
