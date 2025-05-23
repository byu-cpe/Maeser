# Accept from CLI or use defaults
CLASS_DIR ?= uploads/Code
SUBDIRS ?= $(CLASS_DIR)/GroupOne,$(CLASS_DIR)/GroupTwo

# Python scripts
RENAME_SCRIPT = rename_files.py
VECTOR_SCRIPT = vector_store_operator.py

# Main rule
all:
	@echo "Processing CLASS_DIR: $(CLASS_DIR)"
	@echo "Processing SUBDIRS: $(SUBDIRS)"
	@$(MAKE) process SUBDIRS="$(SUBDIRS)"

# Processing each group directory
process:
	@echo "Processing subdirectories in $(CLASS_DIR)..."
	@for dir in $(shell find $(CLASS_DIR) -mindepth 1 -maxdepth 1 -type d); do \
		echo "---- Processing $$dir ----"; \
		\
		echo "1. Renaming PDF files..."; \
		python rename_files.py "$$dir"; \
		\
		echo "2. Converting PDFs to text..."; \
		for pdf in $$dir/*.pdf; do \
			filename=$$(basename $$pdf .pdf); \
			pdftotext "$$pdf" "$$dir/$$filename.txt"; \
		done; \
		\
		echo "3. Running vector store operator..."; \
		python vector_store_operator.py "$$dir"; \
		\
		echo "4. Deleting .txt and .pdf files..."; \
		find "$$dir" -maxdepth 1 -type f \( -name '*.txt' -o -name '*.pdf' \) -delete; \
		\
		echo "✔ Completed $$dir"; \
		echo ""; \
	done

