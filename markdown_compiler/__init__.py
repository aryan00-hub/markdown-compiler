"""
This file contains functions that work on entire documents at a time
(and not line-by-line).
"""

import re

from markdown_compiler.util.line_functions import (
    compile_headers,
    compile_strikethrough,
    compile_bold_stars,
    compile_bold_underscore,
    compile_italic_star,
    compile_italic_underscore,
    compile_code_inline,
    compile_images,
    compile_links,
)


def compile_lines(text):
    r"""
    Apply all markdown transformations to the input text.
    (Handles multiline <p> and multiline code blocks using ``` fences.)
    """
    lines = text.split("\n")

    out = []
    in_paragraph = False
    in_code_block = False

    for raw in lines:
        stripped = raw.strip()

        # --- code fences ---
        if stripped == "```":
            if not in_code_block:
                # opening fence
                in_code_block = True
                out.append("<pre>")
            else:
                # closing fence
                in_code_block = False
                out.append("</pre>")
            continue

        # --- inside code block: DO NOT transform markdown ---
        if in_code_block:
            out.append(raw.rstrip("\n"))
            continue

        # --- blank line closes paragraph ---
        if stripped == "":
            if in_paragraph:
                out.append("</p>")
                in_paragraph = False
            else:
                out.append("")
            continue

        # --- headers should not be inside a paragraph ---
        if stripped.startswith("#"):
            if in_paragraph:
                out.append("</p>")
                in_paragraph = False

            line = stripped
            line = compile_headers(line)
            out.append(line)
            continue

        # --- normal paragraph text ---
        if not in_paragraph:
            in_paragraph = True
            out.append("<p>")

        line = stripped
        line = compile_strikethrough(line)
        line = compile_bold_stars(line)
        line = compile_bold_underscore(line)
        line = compile_italic_star(line)
        line = compile_italic_underscore(line)
        line = compile_code_inline(line)
        line = compile_images(line)
        line = compile_links(line)
        out.append(line)

    if in_code_block:
        out.append("</pre>")

    if in_paragraph:
        out.append("</p>")

    return "\n".join(out)


def markdown_to_html(markdown, add_css):
    """
    Convert the input markdown into valid HTML,
    optionally adding CSS formatting.
    """
    html = """
<html>
<head>
    <style>
    ins { text-decoration: line-through; }
    </style>
"""
    if add_css:
        html += """
<link rel="stylesheet" href="https://izbicki.me/css/code.css" />
<link rel="stylesheet" href="https://izbicki.me/css/default.css" />
"""
    html += """
</head>
<body>
"""
    html += compile_lines(markdown)
    html += """
</body>
</html>
"""
    return html


def minify(html):
    r"""
    Remove redundant whitespace (spaces and newlines) from the input HTML,
    and convert all whitespace characters into spaces.
    """
    return re.sub(r"\s+", " ", html).strip()


def convert_file(input_file, add_css):
    """
    Convert the input markdown file into an HTML file.
    If the input filename is `README.md`,
    then the output filename will be `README.html`.
    """
    if input_file[-3:] != ".md":
        raise ValueError("input_file does not end in .md")

    with open(input_file, "r") as f:
        markdown = f.read()

    html = markdown_to_html(markdown, add_css)
    html = minify(html)

    with open(input_file[:-2] + "html", "w") as f:
        f.write(html)