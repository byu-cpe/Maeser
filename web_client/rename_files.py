import os
import sys

if len(sys.argv) < 2:
    print("Usage: python rename_files.py <directory>")
    sys.exit(1)

target_dir = sys.argv[1]

if not os.path.isdir(target_dir):
    print(f"Error: {target_dir} is not a valid directory.")
    sys.exit(1)

# Collect only .pdf files, sort for consistency
pdf_files = sorted([f for f in os.listdir(target_dir) if f.lower().endswith(".pdf")])

for i, filename in enumerate(pdf_files):
    old_path = os.path.join(target_dir, filename)
    new_name = f"{i+1}.pdf"
    new_path = os.path.join(target_dir, new_name)
    os.rename(old_path, new_path)
    print(f"Renamed {filename} -> {new_name}")
