.. _installation:

Installation of pontos
======================

Requirements
^^^^^^^^^^^^

Python 3.7 and later is supported.

Using pip
^^^^^^^^^

pip 19.0 or later is required.

.. note:: All commands listed here use the general tool names. If some of
 these tools are provided by your distribution, you may need to explicitly use
 the Python 3 version of the tool, e.g. **`pip3`**.

You can install the latest stable release of **pontos** from the Python
Package Index (pypi) using `pip <https://pip.pypa.io/en/stable/>`_

.. code-block:: shell

    pip install --user pontos

Using poetry
^^^^^^^^^^^^^^^^^^^

Because **pontos** is a Python library you most likely need a tool to
handle Python package dependencies and Python environments. Therefore we
strongly recommend using `pipenv <https://pipenv.pypa.io/en/latest/>`_ or `poetry <https://python-poetry.org/>`_.

You can install the latest stable release of **pontos** and add it as
a dependency for your current project using `poetry <https://python-poetry.org/>`_

.. code-block:: shell

    poetry add pontos

For installation via pipenv please take a look at their `documentation <https://pipenv.pypa.io/en/latest/>`_.
