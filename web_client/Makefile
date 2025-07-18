# SPDX-License-Identifier: LGPL-3.0-or-later

# Accept from CLI or use defaults
CLASS_DIR ?= uploads/Code

# Python scripts
RENAME_SCRIPT = rename_files.py
VECTOR_SCRIPT = vector_store_operator.py
FIGURE_SCRIPT = extract_figures.py

# Main rule
all:
	@echo "Processing CLASS_DIR: $(CLASS_DIR)"
	@$(MAKE) process

# Processing each group directory
process:
	@echo "Processing subdirectories in $(CLASS_DIR)..."
	@for dir in $(shell find $(CLASS_DIR) -mindepth 1 -maxdepth 1 -type d); do \
		if [ -f "$$dir/index.faiss" ]; then \
			echo "⚠ dataset for $$dir already exists, skipping."; \
			continue; \
		fi; \
		echo "---- Processing $$dir ----"; \
		\
		echo "1. Renaming PDF files..."; \
		python $(RENAME_SCRIPT) "$$dir"; \
		\
		echo "2. Converting PDFs to text..."; \
		for pdf in $$dir/*.pdf; do \
			filename=$$(basename $$pdf .pdf); \
			pdftotext "$$pdf" "$$dir/$$filename.txt"; \
		done; \
		\
		echo "3. Extracting figures from PDFs..."; \
		python $(FIGURE_SCRIPT) "$$dir"; \
		\
		echo "4. Running vector store operator..."; \
		python $(VECTOR_SCRIPT) "$$dir"; \
		\
		echo "5. Deleting .txt and .pdf files..."; \
		find "$$dir" -maxdepth 1 -type f \( -name '*.txt' -o -name '*.pdf' \) -delete; \
		\
		echo "✔ Completed $$dir"; \
		echo ""; \
	done