import os
import markdown
from shutil import copyfile
def folder_to_html(input_folder, output_folder):
    # Converts all the .md or .png files in the input_folder to .html files in the output_folder
    # input_folder: str, path to the folder containing the .md or .png files
    # output_folder: str, path to the folder where the .html files will be saved
    # Returns: None
    # Get all the files in the input folder
    files = get_folder_files(input_folder)
    # Create the output folder if it does not exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)
    # Convert to html
    convert_to_html(files, output_folder)
    return None

def get_folder_files(folder):
    # For every file in the folder, if it is a .md or .png file, add it to the list
    # For every folder in the file, recursively call the function
    # folder: str, path to the folder
    # Returns: list of str, paths to the files in the folder
    files = []
    for file in os.listdir(folder):
        file_path = os.path.join(folder, file)
        if os.path.isfile(file_path):
            if file.endswith('.md') or file.endswith('.png'):
                files.append(file_path)
        elif os.path.isdir(file_path):
            files.extend(get_folder_files(file_path))
    return files

import os
import re

def group_files_by_top_level_folder(files):
    grouped_files = {}

    # Updated regular expression to match 'Milestone-X' or 'Milestone X'
    milestone_pattern = re.compile(r'Milestone[-\s]*[\d]+')

    for file_path in files:
        # Normalize the file path to handle platform differences (e.g., Windows \ vs. Linux /)
        normalized_path = os.path.normpath(file_path)

        # Split the normalized path
        path_parts = normalized_path.split(os.sep)

        top_level_folder = None

        # Look for a folder that matches 'Milestone-X' or 'Milestone X'
        for part in path_parts:
            if milestone_pattern.match(part):
                top_level_folder = part
                break
        
        if top_level_folder:
            if top_level_folder not in grouped_files:
                grouped_files[top_level_folder] = []
            grouped_files[top_level_folder].append(file_path)
        else:
            # If no 'Milestone' folder found, you can decide what to do (ignore or raise an error)
            pass
    return grouped_files


def convert_markdown_to_html(md_file_path, output_path):
    """
    Convert a markdown file to HTML and save it to the specified output path.
    :param md_file_path: str, path to the markdown file
    :param output_path: str, path to save the converted HTML file
    :return: str, the HTML content
    """
    with open(md_file_path, "r", encoding="utf-8") as f:
        markdown_content = f.read()
    html_content = markdown.markdown(markdown_content)

    # Write the HTML content to file
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    return html_content

def copy_png_file(png_file_path, output_path):
    """
    Copy a PNG file to the output directory.
    :param png_file_path: str, path to the PNG file
    :param output_path: str, path to save the PNG file
    :return: None
    """
    copyfile(png_file_path, output_path)

def create_folder_html(folder, folder_files, output_folder):
    """
    Create an index.html file for a top-level folder, referencing all its HTML files and images.
    :param folder: str, the top-level folder name
    :param folder_files: list of str, list of file paths in this folder
    :param output_folder: str, the folder where the HTML will be saved
    :return: None
    """
    folder_output_path = os.path.join(output_folder, folder)
    os.makedirs(folder_output_path, exist_ok=True)

    index_html_content = f"<h1>{folder}</h1>\n"
    
    for file_path in folder_files:
        file_name = os.path.basename(file_path)

        # If it's a markdown file, convert it and add a reference
        if file_name.endswith(".md"):
            html_file_name = file_name.replace(".md", ".html")
            html_file_path = os.path.join(folder_output_path, html_file_name)
            convert_markdown_to_html(file_path, html_file_path)
            index_html_content += f'<a href="{html_file_name}">{file_name}</a><br>\n'

        # If it's a PNG, copy it and add an image reference
        elif file_name.endswith(".png"):
            png_output_path = os.path.join(folder_output_path, file_name)
            copy_png_file(file_path, png_output_path)
            index_html_content += f'<img src="{file_name}" alt="{file_name}"><br>\n'

    # Write the top-level index.html
    index_html_path = os.path.join(folder_output_path, "index.html")
    with open(index_html_path, "w", encoding="utf-8") as f:
        f.write(index_html_content)

def convert_to_html(files, output_folder):
    """
    Main function to orchestrate the conversion of files to HTML.
    :param files: list of str, paths to the files
    :param output_folder: str, path to the folder where the HTML files will be saved
    :return: None
    """
    # Step 1: Group files by top-level folder
    grouped_files = group_files_by_top_level_folder(files)

    # Step 2: Convert files and create folder-specific index.html files
    for folder, folder_files in grouped_files.items():
        create_folder_html(folder, folder_files, output_folder)

    print(f"Conversion complete. Files saved to {output_folder}")

# Convert documents in the input folder to HTML files in the output folder
if __name__ == '__main__':
    get_app_dir = os.path.abspath(os.path.join(os.getcwd(), "./application/"))
    input_folder = os.path.join(get_app_dir, "static", "Documents")
    output_folder = input_folder + '_as_html'
    print(input_folder, output_folder)
    folder_to_html(input_folder, output_folder)