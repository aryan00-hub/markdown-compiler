'''
This file contains functions that work on entire documents at a time
(and not line-by-line).
'''

from markdown_compiler.util.line_functions import *


def compile_lines(text):
    r'''
    Apply all markdown transformations to the input text.
    '''
    lines = text.split('\n')
    new_lines = []
    in_paragraph = False
    in_code_block = False

    for line in lines:
        raw = line  # preserve indentation for code blocks
        stripped = line.strip()

        # --- fenced code blocks: ``` ... ``` ---
        if stripped.startswith("```"):
            if not in_code_block:
                # starting a code block
                in_code_block = True

                # close paragraph before <pre>
                if in_paragraph:
                    new_lines.append("</p>")
                    in_paragraph = False

                new_lines.append("<pre>")
            else:
                # ending a code block
                in_code_block = False
                new_lines.append("</pre>")
            continue

        # inside code: no formatting, keep exact text
        if in_code_block:
            new_lines.append(raw)
            continue

        # blank line ends a paragraph
        if stripped == "":
            if in_paragraph:
                new_lines.append("</p>")
                in_paragraph = False
            else:
                new_lines.append("")
            continue

        # start paragraph if needed (headers are NOT wrapped in <p>)
        if not stripped.startswith("#") and not in_paragraph:
            in_paragraph = True
            new_lines.append("<p>")

        # apply line-by-line transformations
        out = stripped
        out = compile_headers(out)
        out = compile_strikethrough(out)
        out = compile_bold_stars(out)
        out = compile_bold_underscore(out)
        out = compile_italic_star(out)
        out = compile_italic_underscore(out)
        out = compile_code_inline(out)
        out = compile_images(out)
        out = compile_links(out)

        new_lines.append(out)

    # close final paragraph if file ends inside one
    if in_paragraph:
        new_lines.append("</p>")

    return "\n".join(new_lines)


def markdown_to_html(markdown, add_css):
    '''
    Convert the input markdown into valid HTML,
    optionally adding CSS formatting.

    >>> assert(markdown_to_html('this *is* a _test_', False))
    >>> assert(markdown_to_html('this *is* a _test_', True))
    '''

    html = '''
<html>
<head>
    <style>
    ins { text-decoration: line-through; }
    </style>
    '''
    if add_css:
        html += '''
<link rel="stylesheet" href="https://izbicki.me/css/code.css" />
<link rel="stylesheet" href="https://izbicki.me/css/default.css" />
        '''
    html += '''
</head>
<body>
    ''' + compile_lines(markdown) + '''
</body>
</html>
    '''
    return html


def minify(html):
    r'''
    Remove redundant whitespace (spaces and newlines) from the input HTML,
    and convert all whitespace characters into spaces.

    >>> minify('       ')
    ''
    >>> minify('   a    ')
    'a'
    >>> minify('   a    b        c    ')
    'a b c'
    >>> minify('a b c')
    'a b c'
    >>> minify('a\nb\nc')
    'a b c'
    >>> minify('a \nb\n c')
    'a b c'
    >>> minify('a\n\n\n\n\n\n\n\n\n\n\n\n\n\nb\n\n\n\n\n\n\n\n\n\n')
    'a b'
    '''
    return ' '.join(html.split())


def convert_file(input_file, add_css):
    '''
    Convert the input markdown file into an HTML file.
    If the input filename is `README.md`,
    then the output filename will be `README.html`.
    '''

    # validate that the input file is a markdown file
    if input_file[-3:] != '.md':
        raise ValueError('input_file does not end in .md')

    # load the input file
    with open(input_file, 'r') as f:
        markdown = f.read()

    # generate the HTML from the Markdown
    html = markdown_to_html(markdown, add_css)
    html = minify(html)

    # write the output file
    with open(input_file[:-2] + 'html', 'w') as f:
        f.write(html)