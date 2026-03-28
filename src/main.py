from textnode import TextNode, TextType
import os
import shutil
import sys
from utils import markdown_to_html_node, extract_title

def static_to_public(source, destination):
    root = os.path.abspath(".")
    source_path = os.path.join(root, source)
    destination_path = os.path.join(root, destination)
    if destination == "docs":
        shutil.rmtree(destination_path)
        os.mkdir(destination_path)
    for file in os.listdir(source_path):
        source_file = os.path.join(source_path, file)
        destination_file = os.path.join(destination_path, file)
        if os.path.isdir(source_file):
            os.mkdir(destination_file)
            static_to_public(f"{source}/{file}", f"{destination}/{file}")
        else:
            shutil.copy(source_file, destination_file)

def generate_page(from_path, template_path, dest_path, basepath):
    print(f"Generating page from {from_path} to {dest_path} using {template_path}")

    source_content = ""
    template_content = ""
    with open(from_path) as from_file:
        source_content = from_file.read()
    with open(template_path) as template_file:
        template_content = template_file.read()

    html_content = markdown_to_html_node(source_content).to_html()
    title = extract_title(source_content)
    template_content = template_content.replace("{{ Title }}", title).replace("{{ Content }}", html_content)
    template_content = template_content.replace('href="/', f'href="{basepath}').replace('src="/', f'src="{basepath}')
    os.makedirs("/".join(dest_path.split("/")[:-1]), exist_ok=True)
    with open(dest_path, "w") as file:
        file.write(template_content)

def generate_pages_recursive(dir_path_content, template_path, dest_dir_path, basepath):
    root = os.path.abspath(".")
    source_path = os.path.join(root, dir_path_content)
    destination_path = os.path.join(root, dest_dir_path)
    for file in os.listdir(source_path):
        source_file = os.path.join(source_path, file)
        destination_file = os.path.join(destination_path, file)
        if os.path.isdir(source_file):
            #os.makedirs(destination_file, exist_ok=True)
            generate_pages_recursive(f"{dir_path_content}/{file}", template_path, f"{dest_dir_path}/{file}", basepath)
        else:
            generate_page(f"{dir_path_content}/{file}", template_path, f"{dest_dir_path}/{file.replace(".md", ".html")}", basepath)

def main():
    basepath = sys.argv[1] if len(sys.argv) > 1 else "/"
    static_to_public("static", "docs")
    generate_pages_recursive("content", "template.html", "docs", basepath)

main()
