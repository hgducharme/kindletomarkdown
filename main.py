"""
TODO:
- Some how higlights get out of order by page number, I think that's because Kindle organizes them by the datetime that they are created. Organize them by page number, and then by datetime.
- If the annotation type is a note, then append the note to the previous section
- Sanitize the input file
- Build a front end
- Make sure all the notes are grouped together for the book they correspond to
- Turn bulletpoints into bullet point lists
- For each note, find the associated highlight and have them together in one string

This is how we should transform this program:

This program should read in each annotation. An annotation belongs to a book and has certain meta content associated with it, such as a timestamp, location, page number, etc. We then store each annotation in a hash table (one hash table per book) where the key is the location. Each time we find a new annotation with a location that overlaps with an existing annotation, we append this annotation to the running list of annotations for that location. Only annotations with overlapping locations are considered conflicts and need to be reviewed. We then only keep the annotation with with the most recent timestamp. It is assumed that the last edit made by the user to the annotation will always be the most correct version—-if we want to do this programatically without the use of an LLM.
"""

import pathlib
from enum import StrEnum


class AnnotationType(StrEnum):
    HIGHLIGHT = "Highlight"
    NOTE = "Note"


class Annotation:
    def __init__(
        self,
        type: AnnotationType,
        page_start: int,
        page_end: int,
        location_start: int,
        location_end: int,
        text: str,
    ):
        self.type = type
        self.page_start = page_start
        self.page_end = page_end
        self.location_start = location_start
        self.location_end = location_end
        self.text = text

    def location_range(self) -> str:
        if (self.location_end == None) or (self.location_start == self.location_end):
            return f"{self.location_start}"
        else:
            return f"{self.location_start}-{self.location_end}"

    def page_range(self) -> str:
        if (self.page_end == None) or (self.page_start == self.page_end):
            return f"{self.page_start}"
        else:
            return f"{self.page_start}-{self.page_end}"


class Book:
    def __init__(self, title_and_author: str):
        self.title_and_author = title_and_author
        self.notes = []
        self.highlights = []

    def append(self, annotation: Annotation) -> None:
        if annotation.type == AnnotationType.NOTE:
            self.notes.append(annotation)
        elif annotation.type == AnnotationType.HIGHLIGHT:
            self.highlights.append(annotation)
        else:
            raise Exception(f"Unsupported annotation type: '{annotation.type}'")


def get_location_number_from_string(s):
    return int(s.split(" ")[4].split("-")[0].split("**\n")[0])


def get_location_number_from_annotation(a: Annotation) -> int:
    return a.location_start


def main(input_file_path):
    with open(input_file_path, "r") as file:
        data = file.read()

    books = {}
    notes = []
    highlights = []
    sections = data.strip().split("==========")
    for section in sections:
        lines = section.strip().split("\n")

        # In order for a section to be valid, it must have the following 4 lines:
        # 1) Book title and author
        # 2) Annotation metadata
        # 3) An empty line
        # 4) The annotation itself
        if len(lines) < 4:
            continue

        ###
        # Parse the text from the section
        ###

        title_and_author = lines[0].strip()
        annotation_type = lines[1].split(" ")[2]

        # Using "3:" because the first 3 lines are the title, author, and date, and multiple lines in a note will be separated by an empty line
        annotation = lines[3:]
        annotation = ["\n>\n> " if i == "" else i for i in annotation]
        annotation = "".join(annotation)

        page_range = lines[1].split(" ")[5]
        pages = page_range.split("-")
        page_start = int(pages[0])
        page_end = None if (len(pages) == 1) else int(pages[1])

        location_range = lines[1].split(" ")[8]
        locations = location_range.split("-")
        location_start = int(locations[0])
        location_end = None if (len(locations) == 1) else int(locations[1])

        # Convert the annotation type string to an enum value
        if annotation_type.lower() == "highlight":
            annotation_type = AnnotationType.HIGHLIGHT
        elif annotation_type.lower() == "note":
            annotation_type = AnnotationType.NOTE
        else:
            raise Exception(f"Invalid annotation type: '{annotation_type}'")

        ###
        # Create classes and store the parsed text
        ###

        # Store all the parsed data
        a = Annotation(
            annotation_type,
            page_start,
            page_end,
            location_start,
            location_end,
            annotation,
        )

        if title_and_author in books.keys():
            books[title_and_author].append(a)
        else:
            book = Book(title_and_author)
            book.append(a)
            books[title_and_author] = book

        # Create and store the output string
        output = f"> **Pg. {a.page_range()}, Location {a.location_range()}**\n> \n> {a.text}\n\n"
        if a.type == AnnotationType.NOTE:
            notes.append(output)
        else:
            highlights.append(output)

    # Sort the notes and highlight arrays by page number
    sorted_highlights = sorted(highlights, key=get_location_number_from_string)
    sorted_notes = sorted(notes, key=get_location_number_from_string)
    all = sorted(highlights + notes, key=get_location_number_from_string)

    ###
    # Associate notes with their respective highlights
    ###
    # TODO: We need to find a better way to store the annotation. We need a way to store with locations as keys, and a way to be able to find the location of a highlight that is associated with the location of a note.
    # If this is a note then append it to the associated annotation collection
    # This has to be done after all the sections are read-in. It's possible to come across the note before the associated highlight
    # Also figure out a way to store highlights with the same starting location. It's possible the start of the highlight exists in the same 150-byte block. How do we determine here which highlight the note goes to? For now just say this one can't find a home and inform the user
    # Maybe a dict isn't the right way to go bc the starting locations aren't unique. We might have to have two arrays, one array with the starting locations and one with the annotation, with a one to one correspondence. If we find more than one annotation with the same starting location, we just inform the user. Otherwise, we associate the note with the single highlight found.
    # Read in all the notes and highlights into arrays inside the book class, then sort the arrays, and do the traversing to associate notes with highlights.

    all_notes_and_highlights_associated_together = []
    for book in books.values():
        notes = sorted(book.notes, key=get_location_number_from_annotation)
        highlights = sorted(book.highlights, key=get_location_number_from_annotation)

        notes_used = {}
        for note in notes:
            note_location = note.location_start
            for highlight in highlights:
                highlight_interval = (highlight.location_start, highlight.location_end)
                if (
                    (note_location == highlight.location_start)
                    or (note_location == highlight.location_end)
                    or (
                        (note_location > highlight.location_start)
                        and (note_location < highlight.location_end)
                    )
                ):
                    print(
                        f"\n\nFound a match! Highlight interval: {highlight_interval}. Note location: {note_location}\nHighlight:  {highlight.text}\nNote: {note.text}"
                    )

                    if note_location in notes_used.keys():
                        notes_used[note_location] += 1
                        print(
                            f"Potential duplicate!! We have used this note location {notes_used[note_location]} time(s) now"
                        )
                    else:
                        notes_used[note_location] = 1
                    # TODO: Find a way to associate the note and highlight together. Either in a class, or just combine them into an output string.

    current_directory = pathlib.Path().resolve()
    with open(f"{current_directory}/notes.md", "w") as file:
        file.write("## Highlights\n\n")
        for annotation in sorted_highlights:
            file.write(annotation)

        file.write("## Notes\n\n")
        for annotation in sorted_notes:
            file.write(annotation)

        # for annotation in all:
        #     file.write(annotation)


if __name__ == "__main__":
    input_file_path = "/Users/hgd/Desktop/Clippings/state_cleaned.txt"
    main(input_file_path)
