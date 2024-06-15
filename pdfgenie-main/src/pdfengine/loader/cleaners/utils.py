import re


def basic_cleaner(page: str):
    # Remove multiple newlines
    page = re.sub(r"\n+", "\n", page)
    page_lines = page.split("\n")
    # Remove lines that are contained in the next line
    temp_page = []
    for i in range(len(page_lines)):
        if page_lines[i] == "":
            continue
        elif i + 1 < len(page_lines):
            if page_lines[i] not in page_lines[i + 1]:
                temp_page.append(page_lines[i])
        elif i == len(page_lines) - 1:
            temp_page.append(page_lines[i])
    page = "\n".join([x for x in temp_page if x != "-----" or x != ""])
    return page


def remove_images(page: str):
    # Remove images
    page = re.sub(r"!\[.*\.(jpg|png|gif|bmp|svg|webp)\]\(.*\)", "", page)
    return page


def remove_duplicates(page: str):
    # Remove duplicate lines
    page_lines = page.split("\n")
    page_lines = list(set(page_lines))
    page = "\n".join(page_lines)
    return page
