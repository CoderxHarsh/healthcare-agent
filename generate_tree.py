import os

def generate_tree(root_dir=".", output_file="structure.txt", ignore_dirs=None):
    if ignore_dirs is None:
        ignore_dirs = {".git", "__pycache__", "node_modules", ".venv", "venv", ".env", "dist", "build", ".next", ".mypy_cache"}

    lines = []

    for dirpath, dirnames, filenames in os.walk(root_dir):
        # Remove ignored directories in-place so os.walk skips them
        dirnames[:] = [d for d in dirnames if d not in ignore_dirs]

        # Calculate depth for indentation
        depth = dirpath.replace(root_dir, "").count(os.sep)
        indent = "    " * depth
        folder_name = os.path.basename(dirpath) or root_dir
        lines.append(f"{indent}📁 {folder_name}/")

        sub_indent = "    " * (depth + 1)
        for filename in sorted(filenames):
            lines.append(f"{sub_indent}📄 {filename}")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    print(f"✅ Structure saved to: {output_file}")
    print(f"📊 Total lines: {len(lines)}")

if __name__ == "__main__":
    generate_tree(root_dir=".", output_file="structure.txt")
