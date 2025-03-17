"""
This module provides functions to generate and format output documents for the GPT Batch Policy Processor.
It includes functions to create tables in Word documents, read data from Excel files, and format the output
documents with relevant information and metrics.

Functions:
- get_output_fname: Generates the output file name based on the provided path function and file type.
- create_word_table: Creates a table in a Word document with the provided data.
- format_output_doc: Formats the output Word document with query and variable specifications.
- output_results: Outputs the results to a Word document.
- output_metrics: Outputs processing metrics to a Word document.
"""

from datetime import datetime
from docx.shared import Pt
import os


# Function to generate the output file name based on the provided path function and file type
def get_output_fname(path_fxn, filetype="docx"):
    return path_fxn(f"results.{filetype}")


# Function to create a table in a Word document
# doc: The Word document object
# output_pdf_path: Path to the output PDF file
# rows_dict: Dictionary containing row data
# output_headers: List of column headers
def create_word_doc(doc, output_pdf_path, rows_dict):
    fname = os.path.basename(output_pdf_path)
    doc.add_heading(f"{fname}", 2)
    for title in rows_dict[1]: 
        doc.add_paragraph(title)


# Function to format the output Word document
# output_doc: The Word document object
# gpt_analyzer: The GPT analyzer object containing query and variable specifications
def format_output_doc(output_doc, gpt_analyzer):
    main_query, variable_specs = gpt_analyzer.main_query, gpt_analyzer.variable_specs

    # Add title to the document
    title = output_doc.add_heading(level=0)
    title_run = title.add_run("Results: GPT Batch Headline Processor (beta)")
    title_run.font.size = Pt(24)

    # Add date and query information
    output_doc.add_heading(f"{datetime.today().strftime('%B %d, %Y')}", 1)
    output_doc.add_heading("Query info", 2)
    output_doc.add_paragraph(
        "The following query is run for each of the variable specifications listed below:"
    )
    query_paragraph = output_doc.add_paragraph()
    query_text = main_query.replace("Text: {excerpts}", "")
    query_run = query_paragraph.add_run(query_text)
    query_run.italic = True

    # Add table with variable specifications
    schema_var_names = list(variable_specs.keys())
    num_schema_cols = len(schema_var_names)
    table = output_doc.add_table(rows=num_schema_cols + 1, cols=3)
    table.style = "Table Grid"
    table.cell(0, 0).text = "Variable name"
    table.cell(0, 0).paragraphs[0].runs[0].font.bold = True
    table.cell(0, 1).text = "Variable description (optional)"
    table.cell(0, 1).paragraphs[0].runs[0].font.bold = True
    table.cell(0, 2).text = "Context (optional)"
    table.cell(0, 2).paragraphs[0].runs[0].font.bold = True

    # Populate the table with variable specifications
    try:
        for var_i in range(num_schema_cols):
            var_name = schema_var_names[var_i]
            if len(var_name) > 0:
                table.cell(var_i + 1, 0).text = var_name
                if "variable_description" in variable_specs[var_name]:
                    descr = variable_specs[var_name]["variable_description"]
                    table.cell(var_i + 1, 1).text = descr
                if "context" in variable_specs[var_name]:
                    if len(variable_specs[var_name]["context"]) > 0:
                        context = f"{variable_specs[var_name]['context']}"
                        table.cell(var_i + 1, 2).text = context
    except Exception as e:
        print(f"Error (format_output_doc()): {e}")


# Function to output results to a Word document
# gpt_analyzer: The GPT analyzer object
# output_doc: The Word document object
# output_pdf_path: Path to the output PDF file
# headline_info: The headlines
def output_results(gpt_analyzer, output_doc, output_pdf_path, headline_info):
    # Extract relevant data from headline_info before passing it
    processed_info = []
    for entry in headline_info:
        title = entry.get('title', 'N/A')
        relevance = entry.get('relevant', 'no')
        # Convert relevance dictionary into a readable string
        processed_info.append({
            "Title": title,
            "Relevant": relevance
        })

    rows_dict = gpt_analyzer.get_results(processed_info)
    print("Rows Dict:", rows_dict)
    create_word_doc(output_doc, output_pdf_path, rows_dict)


def output_metrics(doc, num_docs, t, num_pages, failed_pdfs):
    doc.add_heading(
        f"{num_docs} documents ({num_pages} total pages) processed in {t:.2f} seconds",
        4,
    )
    if len(failed_pdfs) > 0:
        doc.add_heading(f"Unable to process the following PDFs: {failed_pdfs}", 4)
