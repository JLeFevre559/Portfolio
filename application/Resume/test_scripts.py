import os
import tempfile
from django.test import TestCase
from shutil import rmtree
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from.scripts.doc_folders_to_html import (get_folder_files, 
                                         group_files_by_top_level_folder,
                                         convert_markdown_to_html,
                                         copy_png_file,
                                         create_folder_html,
                                         convert_to_html,
                                         folder_to_html)


class GetFolderFilesTestCase(TestCase):

    def setUp(self):
        # Create a temporary directory structure
        self.test_dir = tempfile.mkdtemp()

        # Create Milestone 1 -> Test -> test1.md, test1.png
        milestone1_path = os.path.join(self.test_dir, "Milestone 1", "Test")
        os.makedirs(milestone1_path)
        with open(os.path.join(milestone1_path, "test1.md"), "w") as f:
            f.write("# Test 1 Markdown")
        with open(os.path.join(milestone1_path, "test1.png"), "w") as f:
            f.write("PNG content")

        # Create Milestone 2 -> Requirements -> test2.md, test2.png
        milestone2_path = os.path.join(self.test_dir, "Milestone 2", "Requirements")
        os.makedirs(milestone2_path)
        with open(os.path.join(milestone2_path, "test2.md"), "w") as f:
            f.write("# Test 2 Markdown")
        with open(os.path.join(milestone2_path, "test2.png"), "w") as f:
            f.write("PNG content")

    def tearDown(self):
        # Remove the directory after the test
        rmtree(self.test_dir)

    def test_get_folder_files(self):
        # Call the function on the top-level test directory
        result = get_folder_files(self.test_dir)

        # Normalize the paths for cross-platform compatibility
        expected_files = [
            os.path.join(self.test_dir, "Milestone 1", "Test", "test1.md"),
            os.path.join(self.test_dir, "Milestone 1", "Test", "test1.png"),
            os.path.join(self.test_dir, "Milestone 2", "Requirements", "test2.md"),
            os.path.join(self.test_dir, "Milestone 2", "Requirements", "test2.png"),
        ]

        # Sort both lists to ensure order doesn't affect the test
        self.assertEqual(sorted(result), sorted(expected_files))

from django.test import TestCase

class FolderGroupingTest(TestCase):
    def setUp(self):
        # Mock file paths to simulate a folder structure
        self.mock_files = [
            "path/to/Documents/Milestone-1/Test/test1.md",
            "path/to/Documents/Milestone-1/Test/test1.png",
            "path/to/Documents/Milestone-2/Requirements/test2.md",
            "path/to/Documents/Milestone-2/Requirements/test2.png"
        ]
    
    def test_group_files_by_top_level_folder(self):
        # Expected output: grouped by 'Milestone 1' and 'Milestone 2'
        expected_output = {
            'Milestone-1': [
                "path/to/Documents/Milestone-1/Test/test1.md",
                "path/to/Documents/Milestone-1/Test/test1.png"
            ],
            'Milestone-2': [
                "path/to/Documents/Milestone-2/Requirements/test2.md",
                "path/to/Documents/Milestone-2/Requirements/test2.png"
            ]
        }
        
        # Call the function to group the files
        grouped_files = group_files_by_top_level_folder(self.mock_files)
        
        # Check that the result matches the expected output
        self.assertEqual(grouped_files, expected_output)


class MarkdownConversionTest(TestCase):
    def setUp(self):
        # Sample markdown content with headings, lists, and links
        self.sample_markdown = """
# Sample Heading

This is a **bold** statement.

## Unordered List

- Item 1
- Item 2
    - Nested Item

## Ordered List

1. First item
2. Second item

## Links

[Google](https://www.google.com)
"""
        
    def test_convert_markdown_to_html(self):
        self.maxDiff = None  # Allow full diff display in case of failure

        # Create temporary markdown file and output file paths
        with tempfile.NamedTemporaryFile(delete=False, suffix=".md") as temp_md_file:
            temp_md_file.write(self.sample_markdown.encode("utf-8"))
            temp_md_file_path = temp_md_file.name
        
        # Create a temporary file for the HTML output
        with tempfile.NamedTemporaryFile(delete=False, suffix=".html") as temp_html_file:
            temp_html_file_path = temp_html_file.name

        try:
            # Call the function and capture the output
            html_content = convert_markdown_to_html(temp_md_file_path, temp_html_file_path)

            # Expected HTML content with no indentation
            expected_html = """
<h1>Sample Heading</h1>
<p>This is a <strong>bold</strong> statement.</p>
<h2>Unordered List</h2>
<ul>
<li>Item 1</li>
<li>Item 2<ul>
<li>Nested Item</li>
</ul>
</li>
</ul>
<h2>Ordered List</h2>
<ol>
<li>First item</li>
<li>Second item</li>
</ol>
<h2>Links</h2>
<p><a href="https://www.google.com">Google</a></p>
"""
            # Strip whitespaces from both actual and expected HTML
            self.assertEqual(html_content.replace("\n", "").replace("  ", ""),
                             expected_html.replace("\n", "").replace("  ", ""))

            # Check if the HTML file was written correctly
            with open(temp_html_file_path, "r", encoding="utf-8") as html_file:
                written_html_content = html_file.read().strip()
                self.assertEqual(written_html_content.replace("\n", "").replace("  ", ""),
                                 expected_html.replace("\n", "").replace("  ", ""))
        
        finally:
            # Clean up temporary files
            os.remove(temp_md_file_path)
            os.remove(temp_html_file_path)

class CopyPngFileTest(TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = self.create_temp_directory()
        
        # Create a sample PNG file to test
        self.src_file_path = os.path.join(self.test_dir, "test_image.png")
        with open(self.src_file_path, "wb") as f:
            f.write(os.urandom(1024))  # Create a dummy PNG file
        
        # Destination path
        self.dest_file_path = os.path.join(self.test_dir, "copied_image.png")
        
    def tearDown(self):
        # Cleanup the temporary directory after each test
        rmtree(self.test_dir, ignore_errors=True)

    def create_temp_directory(self):
        """Create a temporary directory for testing."""
        temp_dir = os.path.join('test_media', 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir

    def test_copy_png_file_success(self):
        # Test successful copy of the PNG file
        copy_png_file(self.src_file_path, self.dest_file_path)
        
        # Check if the destination file exists
        self.assertTrue(os.path.isfile(self.dest_file_path))
        
        # Check if the files are identical
        with open(self.src_file_path, 'rb') as f1, open(self.dest_file_path, 'rb') as f2:
            self.assertEqual(f1.read(), f2.read())

    def test_copy_png_file_not_exist(self):
        # Test if a FileNotFoundError is raised when the source file does not exist
        with self.assertRaises(FileNotFoundError):
            copy_png_file('non_existing_file.png', self.dest_file_path)        


class CreateFolderHtmlTest(TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = self.create_temp_directory()

        # Create a sample folder structure and files for testing
        self.folder_name = "Milestone-1"
        self.output_folder = os.path.join(self.test_dir, self.folder_name)

        # Create markdown and PNG files
        self.markdown_file_path = os.path.join(self.test_dir, "test_file.md")
        with open(self.markdown_file_path, "w", encoding="utf-8") as f:
            f.write("# Sample Heading\nThis is a **bold** statement.")

        self.png_file_path = os.path.join(self.test_dir, "test_image.png")
        with open(self.png_file_path, "wb") as f:
            f.write(os.urandom(1024))  # Create a dummy PNG file

        # List of files to be processed
        self.folder_files = [self.markdown_file_path, self.png_file_path]

    def tearDown(self):
        # Cleanup the temporary directory after each test
        rmtree(self.test_dir, ignore_errors=True)

    def create_temp_directory(self):
        """Create a temporary directory for testing."""
        temp_dir = os.path.join('test_media', 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir

    def test_create_folder_html(self):
        # Test the create_folder_html function
        create_folder_html(self.folder_name, self.folder_files, self.test_dir)

        # Check if the index.html file was created
        index_html_path = os.path.join(self.output_folder, "index.html")
        self.assertTrue(os.path.isfile(index_html_path))

        # Check the content of the index.html
        with open(index_html_path, "r", encoding="utf-8") as f:
            index_content = f.read()

        expected_index_content = (
            f"<h1>{self.folder_name}</h1>\n"
            f'<a href="test_file.html">test_file.md</a><br>\n'
            f'<img src="test_image.png" alt="test_image.png"><br>\n'
        )
        self.assertEqual(index_content.strip(), expected_index_content.strip())

        # Check if the HTML file for the markdown was created
        expected_html_path = os.path.join(self.output_folder, "test_file.html")
        self.assertTrue(os.path.isfile(expected_html_path))

        # Verify the content of the converted HTML
        with open(expected_html_path, "r", encoding="utf-8") as f:
            html_content = f.read()

        expected_html_content = (
            "<h1>Sample Heading</h1>\n"
            "<p>This is a <strong>bold</strong> statement.</p>\n"
        )
        self.assertEqual(html_content.strip(), expected_html_content.strip())

        # Check if the PNG file was copied
        self.assertTrue(os.path.isfile(os.path.join(self.output_folder, "test_image.png")))  

class ConvertToHtmlTest(TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = self.create_temp_directory()

        # Create sample folder structure and files for testing
        self.files = [
            os.path.join(self.test_dir, "Milestone-1", "test_file_1.md"),
            os.path.join(self.test_dir, "Milestone-1", "test_image_1.png"),
            os.path.join(self.test_dir, "Milestone-2", "test_file_2.md"),
            os.path.join(self.test_dir, "Milestone-2", "test_image_2.png"),
        ]
        
        # Create directories and files
        os.makedirs(os.path.dirname(self.files[0]), exist_ok=True)
        os.makedirs(os.path.dirname(self.files[2]), exist_ok=True)

        with open(self.files[0], "w", encoding="utf-8") as f:
            f.write("# Heading for Milestone 1\nContent for milestone 1.")

        with open(self.files[1], "wb") as f:
            f.write(os.urandom(1024))  # Create a dummy PNG file

        with open(self.files[2], "w", encoding="utf-8") as f:
            f.write("# Heading for Milestone 2\nContent for milestone 2.")

        with open(self.files[3], "wb") as f:
            f.write(os.urandom(1024))  # Create another dummy PNG file

        self.output_folder = os.path.join(self.test_dir, "output")

    def tearDown(self):
        # Cleanup the temporary directory after each test
        rmtree(self.test_dir, ignore_errors=True)

    def create_temp_directory(self):
        """Create a temporary directory for testing."""
        temp_dir = os.path.join('test_media', 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir

    def test_convert_to_html(self):
        # Test the convert_to_html function
        convert_to_html(self.files, self.output_folder)

        # Check if the output folder was created
        self.assertTrue(os.path.isdir(self.output_folder))

        # Check the index.html for Milestone-1
        milestone_1_index_path = os.path.join(self.output_folder, "Milestone-1", "index.html")
        self.assertTrue(os.path.isfile(milestone_1_index_path))

        with open(milestone_1_index_path, "r", encoding="utf-8") as f:
            milestone_1_content = f.read()

        expected_milestone_1_content = (
            "<h1>Milestone-1</h1>\n"
            '<a href="test_file_1.html">test_file_1.md</a><br>\n'
            '<img src="test_image_1.png" alt="test_image_1.png"><br>\n'
        )
        self.assertEqual(milestone_1_content.strip(), expected_milestone_1_content.strip())

        # Check the index.html for Milestone-2
        milestone_2_index_path = os.path.join(self.output_folder, "Milestone-2", "index.html")
        self.assertTrue(os.path.isfile(milestone_2_index_path))

        with open(milestone_2_index_path, "r", encoding="utf-8") as f:
            milestone_2_content = f.read()

        expected_milestone_2_content = (
            "<h1>Milestone-2</h1>\n"
            '<a href="test_file_2.html">test_file_2.md</a><br>\n'
            '<img src="test_image_2.png" alt="test_image_2.png"><br>\n'
        )
        self.assertEqual(milestone_2_content.strip(), expected_milestone_2_content.strip())

        # Check if the HTML files for the markdowns were created
        expected_html_path_1 = os.path.join(self.output_folder, "Milestone-1", "test_file_1.html")
        self.assertTrue(os.path.isfile(expected_html_path_1))

        expected_html_path_2 = os.path.join(self.output_folder, "Milestone-2", "test_file_2.html")
        self.assertTrue(os.path.isfile(expected_html_path_2))  


class FolderToHtmlTest(TestCase):
    def setUp(self):
        # Create a temporary directory for testing
        self.test_dir = self.create_temp_directory()

        # Create a sample input folder structure and files for testing
        self.input_folder = os.path.join(self.test_dir, "input")
        os.makedirs(self.input_folder)

        self.files = [
            os.path.join(self.input_folder, "Milestone-1", "test_file_1.md"),
            os.path.join(self.input_folder, "Milestone-1", "test_image_1.png"),
            os.path.join(self.input_folder, "Milestone-2", "test_file_2.md"),
            os.path.join(self.input_folder, "Milestone-2", "test_image_2.png"),
        ]

        # Create directories and files
        os.makedirs(os.path.dirname(self.files[0]), exist_ok=True)
        os.makedirs(os.path.dirname(self.files[2]), exist_ok=True)

        with open(self.files[0], "w", encoding="utf-8") as f:
            f.write("# Heading for Milestone 1\nContent for milestone 1.")

        with open(self.files[1], "wb") as f:
            f.write(os.urandom(1024))  # Create a dummy PNG file

        with open(self.files[2], "w", encoding="utf-8") as f:
            f.write("# Heading for Milestone 2\nContent for milestone 2.")

        with open(self.files[3], "wb") as f:
            f.write(os.urandom(1024))  # Create another dummy PNG file

        self.output_folder = os.path.join(self.test_dir, "output")

    def tearDown(self):
        # Cleanup the temporary directory after each test
        rmtree(self.test_dir, ignore_errors=True)

    def create_temp_directory(self):
        """Create a temporary directory for testing."""
        temp_dir = os.path.join('test_media', 'temp')
        os.makedirs(temp_dir, exist_ok=True)
        return temp_dir

    def test_folder_to_html(self):
        # Test the folder_to_html function
        folder_to_html(self.input_folder, self.output_folder)

        # Check if the output folder was created
        self.assertTrue(os.path.isdir(self.output_folder))

        # Check the index.html for Milestone-1
        milestone_1_index_path = os.path.join(self.output_folder, "Milestone-1", "index.html")
        self.assertTrue(os.path.isfile(milestone_1_index_path))

        with open(milestone_1_index_path, "r", encoding="utf-8") as f:
            milestone_1_content = f.read()

        expected_milestone_1_content = (
            "<h1>Milestone-1</h1>\n"
            '<a href="test_file_1.html">test_file_1.md</a><br>\n'
            '<img src="test_image_1.png" alt="test_image_1.png"><br>\n'
        )
        self.assertEqual(milestone_1_content.strip(), expected_milestone_1_content.strip())

        # Check the index.html for Milestone-2
        milestone_2_index_path = os.path.join(self.output_folder, "Milestone-2", "index.html")
        self.assertTrue(os.path.isfile(milestone_2_index_path))

        with open(milestone_2_index_path, "r", encoding="utf-8") as f:
            milestone_2_content = f.read()

        expected_milestone_2_content = (
            "<h1>Milestone-2</h1>\n"
            '<a href="test_file_2.html">test_file_2.md</a><br>\n'
            '<img src="test_image_2.png" alt="test_image_2.png"><br>\n'
        )
        self.assertEqual(milestone_2_content.strip(), expected_milestone_2_content.strip())

        # Check if the HTML files for the markdowns were created
        expected_html_path_1 = os.path.join(self.output_folder, "Milestone-1", "test_file_1.html")
        self.assertTrue(os.path.isfile(expected_html_path_1))

        expected_html_path_2 = os.path.join(self.output_folder, "Milestone-2", "test_file_2.html")
        self.assertTrue(os.path.isfile(expected_html_path_2))