from pathlib import Path

def copy_code_files_as_text(source_dir, output_dir):
    """
    Iterates through the source directory, reads code files (Python, C++ headers, and C++ sources),
    and creates text copies in the output directory while maintaining the project hierarchy.

    :param source_dir: Path to the root directory of the project.
    :param output_dir: Path to the output directory where text files will be saved.
    """
    # Convert inputs to Path objects
    source_dir = Path(source_dir)
    output_dir = Path(output_dir)

    # Define the file extensions to process
    supported_extensions = {'.py', '.h', '.hpp', '.cpp'}

    # Walk through the source directory
    for source_path in source_dir.rglob('*'):
        if source_path.is_file() and source_path.suffix in supported_extensions:
            # Compute the relative path to maintain the hierarchy
            relative_path = source_path.relative_to(source_dir)
            output_path = output_dir / relative_path.with_suffix(relative_path.suffix + '.txt')

            # Ensure the output directory exists
            output_path.parent.mkdir(parents=True, exist_ok=True)

            # Read the content of the file
            try:
                content = source_path.read_text(encoding='utf-8')

                # Write the content to a text file in the output directory
                output_path.write_text(content, encoding='utf-8')

                print(f"Copied: {source_path} -> {output_path}")
            except Exception as e:
                print(f"Error processing file {source_path}: {e}")

if __name__ == "__main__":
    # Define the source and output directories
    source_directory = "include/knowrob"  # Replace with your project path
    output_directory = "include_files"  # Replace with your desired output path

    # Call the function to copy code files as text
    copy_code_files_as_text(source_directory, output_directory)
