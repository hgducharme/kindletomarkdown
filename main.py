"""
TODO:
1) Some how higlights get out of order by page number, I think that's because Kindle organizes them by the datetime that they are created. Organize them by page number, and then by datetime.
2) If the annotation type is a note, then append the note to the previous section
3) Sanitize the input file
4) Write and return a markdown file, or just spit out markdown
5) Build a front end
6) Make sure all the notes are grouped together for the book they correspond to
7) Turn bulletpoints into bullet point lists
"""

import pathlib

def get_page_number_from_string(s):
    return int(s.split(' ')[2].split()[0])

current_directory = pathlib.Path().resolve()
file_path = '/Users/hgd/Desktop/My Clippings.txt'

if __name__ == "__main__":
    with open(file_path, 'r') as file:
        data = file.read()

    sections = data.strip().split("==========")
    notes = []
    highlights = []

    for section in sections:
        lines = section.strip().split("\n")
        if len(lines) >= 4:
            title_and_author = lines[0].strip()
            annotation_type = lines[1].split(" ")[2]
            annotation = lines[-1]

            page_range = lines[1].split(" ")[5]
            pages = page_range.split("-")
            location = lines[1].split(" ")[8]

            if (len(pages) > 1 and (int(pages[0]) == int(pages[1]))):
                page_range = pages[0]
            
            # If this is a note then append it the associated annotation
            output = f"> Page {page_range}\n>\n> {annotation}\n"
            if (annotation_type.lower() == "note"):
                notes.append(output)
            else:
                highlights.append(output)

    # Sort the notes and highlight arrays by page number
    sorted_highlights = sorted(highlights, key=get_page_number_from_string)
    sorted_notes = sorted(notes, key=get_page_number_from_string)

    with open(f"{current_directory}/notes.md", 'w') as file:
        file.write("# Highlights\n\n")
        for annotation in sorted_highlights:
            file.write(annotation + '\n')

        file.write("# Notes\n\n")
        for annotation in sorted_notes:
            file.write(annotation + '\n')