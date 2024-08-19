"""
TODO:
1) Some how higlights get out of order by page number, I think that's because Kindle organizes them by the datetime that they are created. Organize them by page number, and then by datetime.
2) If the annotation type is a note, then append the note to the previous section
3) Sanitize the input file
4) Write and return a markdown file, or just spit out markdown
5) Build a front end
6) Make sure all the notes are grouped together for the book they correspond to
7) Turn bulletpoints into bullet point lists

This is how we should transform this program:

This program should read in each annotation. An annotation belongs to a book and has certain meta content associated with it, such as a timestamp, location, page number, etc. We then store each annotation in a hash table (one hash table per book) where the key is the location. Each time we find a new annotation with a location that overlaps with an existing annotation, we append this annotation to the running list of annotations for that location. Only annotations with overlapping locations are considered conflicts and need to be reviewed. We then only keep the annotation with with the most recent timestamp. It is assumed that the last edit made by the user to the annotation will always be the most correct version—-if we want to do this programatically without the use of an LLM. 
"""

import pathlib


def get_location_number_from_string(s):
    return int(s.split(" ")[4].split("-")[0].split("**\n")[0])


current_directory = pathlib.Path().resolve()
file_path = "/Users/hgd/repos/kindletomarkdown/clippings.txt"

if __name__ == "__main__":
    with open(file_path, "r") as file:
        data = file.read()

    sections = data.strip().split("==========")
    notes = []
    highlights = []

    for section in sections:
        lines = section.strip().split("\n")
        if len(lines) >= 4:
            title_and_author = lines[0].strip()
            annotation_type = lines[1].split(" ")[2]

            # Using "3:" because the first 3 lines are the title, author, and date, and multiple lines in a note will be separated by an empty line
            annotation = lines[3:]
            annotation = ["\n>\n> " if i == "" else i for i in annotation]
            annotation = "".join(annotation)

            page_range = lines[1].split(" ")[5]
            pages = page_range.split("-")
            location_range = lines[1].split(" ")[8]
            locations = location_range.split("-")

            if len(pages) > 1 and (int(pages[0]) == int(pages[1])):
                page_range = pages[0]
            elif len(pages) == 1:
                page_range = pages[0]
            else:
                page_range = f"{pages[0]}-{pages[1]}"

            if len(locations) > 1 and (int(locations[0]) == int(locations[1])):
                location_range = locations[0]
            elif len(locations) == 1:
                location_range = locations[0]
            else:
                location_range = f"{locations[0]}-{locations[1]}"

            # If this is a note then append it to the associated annotation collection
            output = f"> **Pg. {page_range}, Location {location_range}**\n> \n> {annotation}\n\n"
            if annotation_type.lower() == "note":
                notes.append(output)
            else:
                highlights.append(output)

    # Sort the notes and highlight arrays by page number
    sorted_highlights = sorted(highlights, key=get_location_number_from_string)
    sorted_notes = sorted(notes, key=get_location_number_from_string)
    all = sorted(highlights + notes, key=get_location_number_from_string)

    with open(f"{current_directory}/notes.md", "w") as file:
        file.write("## Highlights\n\n")
        # for annotation in sorted_highlights:
        #     file.write(annotation)

        # file.write("## Notes\n\n")
        # for annotation in sorted_notes:
        #     file.write(annotation)

        for annotation in all:
            file.write(annotation)
