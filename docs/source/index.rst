.. Proof Data Analysis documentation master file, created by
   sphinx-quickstart on Fri Nov  4 10:06:13 2022.
   You can adapt this file completely to your liking, but it should at least
   contain the root `toctree` directive.

Welcome to Proof Data Analysis's documentation!
===============================================

Documented here are all of the functions that you will need for data visualization
and analysis.

Make sure to read the data section first to understand how to obtain the data, 
and how it is formatted.

Here is some information on installation and development:


Installation
************

The easiest way to install Proof Data Analysis is to do so straight from Github

.. code-block:: bash

   pip install git+https://github.com/code-keylogger/Data-Analysis.git

You can also install for local development via:

.. code-block:: bash

   cd Data-Analysis
   pip install -e .

Basic Usage
************   

To see a complete example of all functionality being used, see the example in
`docs/scripts/gen_images.ipynb`.


Documentation
************************

This project uses Sphinx, a documentation tool that builds a website from the source code.
To run the documentation website locally, do the following (make sure you are at the package root)

.. code-block:: bash

   pip install sphinx-autobuild
   sphinx-autobuild docs/source build/

Styling
************

To perform code styling, do the following (make sure you are at the package root):

.. code-block:: bash

   make



.. toctree::
   :maxdepth: 2
   :caption: Contents:

   data.rst
   plotting.rst
   clustering.rst
   statistics.rst
   replay.rst
   
