
.. _tools:

Tools and Utilities
====================

:program:`pontos` comes with a continiously increasing set of features.
The following commands are currently available:

* :ref:`pontos-release <pontos-release>`
* :ref:`pontos-version <pontos-version>`
* :ref:`pontos-update-header <pontos-update-header>`
* :ref:`pontos-changelog <pontos-changelog>`
* :ref:`pontos-github <pontos-github>`
* :ref:`pontos-terminal <pontos-terminal>`
* :ref:`pontos-api <pontos-api>`

.. _pontos-release:

pontos-release
---------------

``pontos-release`` - Release handling utility for C and Python Projects

.. note:: 
	We also provide easy-to-use `GitHub Actions <https://github.com/greenbone/actions/#usage>`_, that we recommended to use instead of manually releasing with pontos-release.

.. code-block:: shell

	# Prepare the next patch release (x.x.2) of project <foo>, use conventional commits for 	release notes / commits release
	pontos-release prepare --project <foo> -patch -CC
	# Release that patch version of project <foo> / pushes release
	pontos-release release --project <foo>
	# Sign a release:
	pontos-release sign --project <foo> --release-version 1.2.3 
	--signing-key 1234567890ABCDEFEDCBA0987654321 [--passphrase <for_that_key>]

`pontos-release` will automatically create a changelog (.md-file) when executed

.. _pontos-version:

pontos-version
---------------

``pontos-version`` - Version handling utility for C, Go and Python Projects
.. code-block:: shell

	# Update version of this project to 22.1.1
	pontos-version update 22.1.1
	# Show current projects version
	pontos-version show


**Supported config files:**
``CMakeLists.txt``
``pyproject.toml``
``go.md``
``package.json``


.. _pontos-update-header:

pontos-update-header
--------------------

``pontos-update-header`` - Handling Copyright header for various file types and licences
.. note:: We also provide easy-to-use `GitHub Actions <https://github.com/greenbone/actions/#usage>`_, that updates copyright year in header of files and creates a Pull Request.

.. code-block:: shell

	# Update year in Copyright header in files based on last commit in corresponding repo,
	also add missing headers
	pontos-update-header -d <dir1> <dir2>

**Supported files:**
``.bash``
``.c``
``.h``
``.go``
``.cmake``
``.js``
``.nasl``
``.po``
``.py``
``.sh``
``.txt``
``.xml``
``.xsl``

**Supported licenses:**
``AGPL-3.0-or-later``
``GPL-2.0-only``
``GPL-2.0-or-later``
``GPL-3.0-or-later``

**Copyright header shema:** `Copyright (C) 2020-2022 Greenbone Networks GmbH`

.. _pontos-changelog:

pontos-changelog
----------------

``pontos-changelog`` - Parse conventional commits in the current branch, creating CHANGELOG.md file

.. code-block:: shell

	# Parse conventional commits and create <changelog_file>
	pontos-changelog -o <changelog-file>


.. _pontos-github:

pontos-github
--------------

``pontos-github`` - Handling GitHub operations, like Pull Requests (beta)

.. code-block:: shell

	# create a PR on GitHub
	pontos-github pr create <orga/repo> <head> <target> <pr_title> [--body <pr_body>]
	# update a PR on GitHub
	pontos-github pr update <orga/repo> <pr> [--target <target_branch>] [--title <pr_title>] 	[--body <pr_body>]
	# get modified and deleted files in a PR, store in file test.txt
	pontos-github FS <orga/repo> <pull_request> -s modified deleted -o test.txt
	# add labels to an Issue/PR
	pontos-github L <orga/repo> <issue/PR> label1 label2

.. _pontos-terminal:

pontos-terminal
---------------

``pontos`` also comes with a Terminal interface printing prettier outputs

.. code-block:: python
	
	import pontos.terminal.terminal

	term = terminal.Terminal()
	with term.indent():
    		term.ok("Hello indented World")


.. _pontos-api:

pontos-api
----------

``pontos`` also comes with git and GitHub APIs

.. code-block:: python

	import pontos.git
	import pontos.github

