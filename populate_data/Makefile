SOURCE_DIR := source
OUTPUT_DIR := output
DATA_STORE_DIR := data_stores
DELETION_LOG := $(OUTPUT_DIR)/files_converted.log

PDF_FILES := $(wildcard $(SOURCE_DIR)/*.pdf)
TXT_FILES := $(patsubst $(SOURCE_DIR)/%.pdf, $(OUTPUT_DIR)/%.txt, $(PDF_FILES))

all: vector_store

# Convert PDF to text and remove original PDF
$(OUTPUT_DIR)/%.txt: $(SOURCE_DIR)/%.pdf | $(OUTPUT_DIR)
	pdftotext "$<" "$@"
	rm "$<"

# Only convert if PDFs exist
text: check_pdfs $(TXT_FILES)

# Chunk text files
chunks: text
	python3 doc_chunker_operator.py

# Vector store and cleanup
vector_store: chunks | $(DATA_STORE_DIR)
	@echo "Running vector store operator..."
	python3 vector_store_operator.py && $(MAKE) cleanup_output

# Delete .txt files and log what was deleted
cleanup_output:
	@TXT_TO_DELETE=$$(ls $(OUTPUT_DIR)/*.txt 2>/dev/null || true); \
	if [ -z "$$TXT_TO_DELETE" ]; then \
		echo "No .txt files to delete in $(OUTPUT_DIR)/"; \
	else \
		echo "Deleting text files from $(OUTPUT_DIR)/ and logging..."; \
		for file in $$TXT_TO_DELETE; do \
			echo "$$file" >> $(DELETION_LOG); \
			rm -f "$$file"; \
		done; \
		echo "Deleted $$(echo "$$TXT_TO_DELETE" | wc -l) files. Log saved to $(DELETION_LOG)."; \
	fi

# Ensure necessary directories exist
$(OUTPUT_DIR):
	mkdir -p $(OUTPUT_DIR)

$(DATA_STORE_DIR):
	mkdir -p $(DATA_STORE_DIR)

# Check if PDFs exist before proceeding
check_pdfs:
	@if [ -z "$(PDF_FILES)" ]; then \
		echo "No PDF files found in $(SOURCE_DIR). Skipping processing."; \
		exit 0; \
	fi

clean:
	rm -rf $(OUTPUT_DIR) $(DATA_STORE_DIR)

.PHONY: all text chunks vector_store clean check_pdfs cleanup_output
