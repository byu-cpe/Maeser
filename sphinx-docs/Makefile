# Minimal makefile for Sphinx documentation
#

# You can set these variables from the command line, and also
# from the environment for the first two.
SPHINXOPTS    ?= 
SPHINXBUILD   ?= sphinx-build
SOURCEDIR     = .
BUILDDIR      = _build

PACKAGE_DIR := ../maeser/

PACKAGE_DOC_DIR := autodoc/maeser

PIP := pip

# Valid Sphinx targets
SPHINX_TARGETS := html dirhtml singlehtml pickle json htmlhelp qthelp devhelp epub latex latexpdf latexpdfja text man texinfo info gettext changes xml pseudoxml linkcheck doctest coverage

# Put it first so that "make" without argument is like "make help".
help:
	@$(SPHINXBUILD) -M help "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)

apidoc:
	sphinx-apidoc -fMe -o $(PACKAGE_DOC_DIR) $(PACKAGE_DIR)

tidy: Makefile
	$(SPHINXBUILD) -M clean "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O);

clean: tidy
	rm -rf $(PACKAGE_DOC_DIR)

deps:
	$(PIP) install sphinx sphinx_rtd_theme myst_parser sphinx-book-theme

.PHONY: help apidoc tidy clean Makefile $(SPHINX_TARGETS)

# Catch-all target: route all unknown targets to Sphinx using the new
# "make mode" option.  $(O) is meant as a shortcut for $(SPHINXOPTS).
$(SPHINX_TARGETS): Makefile apidoc
	@$(SPHINXBUILD) -M $@ "$(SOURCEDIR)" "$(BUILDDIR)" $(SPHINXOPTS) $(O)
