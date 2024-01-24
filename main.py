import sys
import PyPDF2
import json
import pdfplumber

def extract_specific_title(pdf_path):
    try:
        # Open the PDF file
        with open(pdf_path, 'rb') as pdf_file:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(pdf_file)

            # Assume the text is on the first page (index 0, 0-indexed)
            page = pdf_reader.pages[0]

            # Extract text from the page
            text = page.extract_text()

            # Split the text into lines
            lines = text.splitlines()

            # Combine lines into title and content_id
            title = ' '.join(lines[:-1])
            content_id = lines[-1]

            # Extract text from the second page (index 1, 0-indexed)
            page1 = pdf_reader.pages[1]
            text_page1 = page1.extract_text()

            # Split the text from the second page into lines
            lines_page1 = text_page1.splitlines()

            all_values = lines_page1

            data_fields = [
                'Level',
                'Sector',
                'Internal/External',
                'Qualification Type',
                'Assessment Language',
                'Recommended Minimum Age',
                'Total Credits',
                'Operational Start Date',
                'Assessment Methods',
                'Qualification Status'
            ]

            split_substrings = ['570', 'Pass/Fail']

            # Iterate through the list and split values based on substrings
            modified_values = []

            for value in all_values:
                for substring in split_substrings:
                    if substring in value:
                        parts = value.split(substring)
                        modified_values.append(substring)
                        modified_values.extend([part.strip() for part in parts])
                        break
                else:
                    modified_values.append(value)

            # Find all values from all_values that are in data_fields
            indices = [modified_values.index(value) for value in data_fields if value in modified_values]

            data={}
            for i in range(len(indices)-1):
                key = modified_values[indices[i]]
                ind = modified_values.index(key)
                data[key] = modified_values[ind+1]


            page2 = pdf_reader.pages[3]
            text = page2.extract_text()

            guidelines = text.find("Brand Guidelines")
            if guidelines != -1:
                guideline_paragraph = text[guidelines+len("Brand Guidelines")+1:guidelines + guidelines]

            mandatory_units_table = []
            optional_units_table = []

            with pdfplumber.open(pdf_path) as pdf:
                for page_num in range(len(pdf.pages)):
                    page = pdf.pages[page_num]
                    text = page.extract_text()
                    table = page.extract_tables()

                    if "Mandatory Units" in text:
                        current_table = mandatory_units_table

                    if table and current_table is not None:
                        current_table.extend(table[0])
                    if "Optional Units" in text and "There are no optional units for this qualification" not in text:
                        current_table = optional_units_table
                        if table and current_table is not None:
                            current_table.extend(table[len(table)-1])

            header = ['Unit ref.', 'Title', 'Level', 'GLH', 'Credit Value']
            converted_data_mandatory_units = []
            converted_data_optional_units = []

            if mandatory_units_table:
                data_rows = mandatory_units_table[1:]

                for row in data_rows:
                    entry = {header[i]: row[i] for i in range(len(header))}
                    converted_data_mandatory_units.append(entry)

            if optional_units_table:
                data_rows = optional_units_table[1:]
                for row in data_rows:
                    entry = {header[i]: row[i] for i in range(len(header))}
                    converted_data_optional_units.append(entry)


            return {"id": content_id, "title": title, **data, "Brand Guidelines": guideline_paragraph, "Mandatory units": converted_data_mandatory_units, "Optional units": converted_data_optional_units}

    except FileNotFoundError:
        print(f"Error: The file '{pdf_path}' was not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

    return None

def save_to_json_file(data, file_path):
    with open(file_path, 'w', encoding='utf-8') as json_file:
        json.dump(data, json_file, indent=2)

def main():
    # Check if the correct number of command-line arguments is provided
    if len(sys.argv) != 2:
        print("Usage: python script_name.py <pdf_path>")
        sys.exit(1)

    # Get the PDF path from the command-line arguments
    pdf_path = sys.argv[1]

    # Call the function with the provided PDF path
    title_data = extract_specific_title(pdf_path)

    if title_data is not None:
        save_to_json_file(title_data, 'temp.json')
    else:
        print("Extraction failed.")

if __name__ == "__main__":
    main()
