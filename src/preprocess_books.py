import os
import re

def remove_header_footer(text):
    # Regular expressions for the start and end of the header and footer
    header_pattern = r"The Project Gutenberg eBook of [^\n]*\n.*\*End of Header"
    footer_pattern = r"\*\*\* END OF THE PROJECT GUTENBERG EBOOK[^\n].*subscribe to our email newsletter to hear about new eBooks\."

    # Remove header and footer by replacing with empty string
    text = re.sub(header_pattern, "", text, flags=re.DOTALL)
    text = re.sub(footer_pattern, "", text, flags=re.DOTALL)

    return text

def process_gutenberg_ebook(file_path, output_dir):
    """Processes the ebook by opening it for reading, removing the header & footer,
    and saving the cleaned content into a new file."""
    # Open file for reading
    with open(file_path, 'r', encoding='utf-8') as file:
        ebook_content = file.read()

    # Call function to remove header & footer
    cleaned_content = remove_header_footer(ebook_content)

    # Construct the output file path
    output_filename = os.path.basename(file_path)
    output_filename = os.path.splitext(output_filename)[0] + "_cleaned.txt"
    output_file_path = os.path.join(output_dir, output_filename)

    # Write the cleaned content to a new file
    with open(output_file_path, 'w', encoding='utf-8') as file:
        file.write(cleaned_content)
    print(f"Cleaned and saved: {output_filename}")

def main():
    # Directory containing Project Gutenberg ebooks
    ebooks_directory = "text_analytics_alice"

    # Directory to save cleaned files
    output_directory = "cleaned_books"

    # Create the output directory if it does not exist
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)

    # Iterate through each file in the directory
    for filename in os.listdir(ebooks_directory):
        if filename.endswith(".txt"):
            # Process each Project Gutenberg ebook file
            file_path = os.path.join(ebooks_directory, filename)
            process_gutenberg_ebook(file_path, output_directory)

if __name__ == "__main__":
    main()
