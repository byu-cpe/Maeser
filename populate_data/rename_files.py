import os

file_num = 0
pwd = "source"

# For each file in the directory, rename a new integer.
for filename in os.listdir(pwd):
    filename.replace(filename, str(file_num)+".pdf")
    os.rename(os.path.join(pwd, filename ), os.path.join(pwd, str(file_num)+".pdf"))
    file_num+=1