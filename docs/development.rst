.. _development:

Development
============

**pontos** uses `poetry <https://python-poetry.org/>`_ for its own dependency management and build
process.

First install poetry via pip

.. code-block:: shell   
   
    pip install --user poetry

Afterwards run

.. code-block:: shell

    poetry install

in the checkout directory of **pontos** (the directory containing the
`pyproject.toml` file) to install all dependencies including the packages only
required for development.

Afterwards activate the git hooks for auto-formatting and linting via `autohooks <https://github.com/greenbone/autohooks/>`_.

.. code-block:: shell

    poetry run autohooks activate

Validate the activated git hooks by running

.. code-block:: shell

    poetry run autohooks check

