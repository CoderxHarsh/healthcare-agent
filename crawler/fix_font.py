import os

file_path = os.path.join('backend', 'pdf_generator.py')
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

content = content.replace('"Arial"', '"DejaVu"')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Replaced Arial with DejaVu")
