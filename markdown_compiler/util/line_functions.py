'''
Each of the functions in this file takes a single line of input and transforms the line in some way.
'''


def compile_headers(line):
    '''
    Convert markdown headers into <h1>,<h2>,etc tags.

    >>> compile_headers('# This is the main header')
    '<h1> This is the main header</h1>'
    >>> compile_headers('## This is a sub-header')
    '<h2> This is a sub-header</h2>'
    >>> compile_headers('### This is a sub-header')
    '<h3> This is a sub-header</h3>'
    >>> compile_headers('#### This is a sub-header')
    '<h4> This is a sub-header</h4>'
    >>> compile_headers('##### This is a sub-header')
    '<h5> This is a sub-header</h5>'
    >>> compile_headers('###### This is a sub-header')
    '<h6> This is a sub-header</h6>'
    >>> compile_headers('      # this is not a header')
    '      # this is not a header'
    '''
    if not line.startswith('#'):
        return line

    n = 0
    while n < len(line) and n < 6 and line[n] == '#':
        n += 1

    if n < len(line) and line[n] == ' ':
        return f'<h{n}>{line[n:]}</h{n}>'

    return line


def compile_bold_stars(line):
    """Convert **bold** to <b>bold</b> (can occur multiple times)."""
    delim = '**'
    out = ''
    i = 0
    while i < len(line):
        if line.startswith(delim, i):
            j = line.find(delim, i + 2)
            if j == -1:
                out += line[i:]
                break
            inner = line[i + 2:j]
            out += '<b>' + inner + '</b>'
            i = j + 2
        else:
            out += line[i]
            i += 1
    return out


def compile_bold_underscore(line):
    """Convert __bold__ to <b>bold</b> (can occur multiple times)."""
    delim = '__'
    out = ''
    i = 0
    while i < len(line):
        if line.startswith(delim, i):
            j = line.find(delim, i + 2)
            if j == -1:
                out += line[i:]
                break
            inner = line[i + 2:j]
            out += '<b>' + inner + '</b>'
            i = j + 2
        else:
            out += line[i]
            i += 1
    return out


def compile_strikethrough(line):
    """Convert ~~strike~~ to <ins>strike</ins> (can occur multiple times)."""
    delim = '~~'
    out = ''
    i = 0
    while i < len(line):
        if line.startswith(delim, i):
            j = line.find(delim, i + 2)
            if j == -1:
                out += line[i:]
                break
            inner = line[i + 2:j]
            out += '<ins>' + inner + '</ins>'
            i = j + 2
        else:
            out += line[i]
            i += 1
    return out


def compile_italic_star(line):
    """
    Convert *italic* to <i>italic</i>, BUT do NOT treat **bold** as italics.
    Handles multiple occurrences.
    """
    out = ''
    i = 0
    while i < len(line):
        if line[i] == '*' and not (i + 1 < len(line) and line[i + 1] == '*'):
            j = i + 1
            while j < len(line):
                if line[j] == '*' and not (j + 1 < len(line) and line[j + 1] == '*'):
                    inner = line[i + 1:j]
                    out += '<i>' + inner + '</i>'
                    i = j + 1
                    break
                j += 1
            else:
                out += line[i:]
                break
        else:
            out += line[i]
            i += 1
    return out


def compile_italic_underscore(line):
    """
    Convert _italic_ to <i>italic</i>, BUT do NOT treat __bold__ as italics.
    Handles multiple occurrences.
    """
    out = ''
    i = 0
    while i < len(line):
        if line[i] == '_' and not (i + 1 < len(line) and line[i + 1] == '_'):
            j = i + 1
            while j < len(line):
                if line[j] == '_' and not (j + 1 < len(line) and line[j + 1] == '_'):
                    inner = line[i + 1:j]
                    out += '<i>' + inner + '</i>'
                    i = j + 1
                    break
                j += 1
            else:
                out += line[i:]
                break
        else:
            out += line[i]
            i += 1
    return out


def compile_code_inline(line):
    """
    Convert `code` to <code>code</code>.
    Must ignore fenced blocks starting with ``` (doctests expect unchanged).
    Inside code spans, escape &, <, >.
    Handles multiple code spans per line.
    """
    if line.startswith('```'):
        return line

    out = ''
    i = 0
    while i < len(line):
        if line[i] == '`':
            j = line.find('`', i + 1)
            if j == -1:
                out += line[i:]
                break
            code = line[i + 1:j]
            code = code.replace('&', '&amp;')
            code = code.replace('<', '&lt;').replace('>', '&gt;')
            out += '<code>' + code + '</code>'
            i = j + 1
        else:
            out += line[i]
            i += 1
    return out


def compile_links(line):
    """
    Convert [text](url) to <a href="url">text</a>.
    Should NOT convert images (which start with ![).
    Handles multiple links per line.
    """
    out = ''
    i = 0
    while i < len(line):
        if line[i] == '[':
            if i > 0 and line[i - 1] == '!':
                out += line[i]
                i += 1
                continue

            rb = line.find(']', i + 1)
            if rb == -1:
                out += line[i:]
                break

            if rb + 1 >= len(line) or line[rb + 1] != '(':
                out += line[i]
                i += 1
                continue

            rp = line.find(')', rb + 2)
            if rp == -1:
                out += line[i:]
                break

            text = line[i + 1:rb]
            url = line[rb + 2:rp]
            out += f'<a href="{url}">{text}</a>'
            i = rp + 1
        else:
            out += line[i]
            i += 1
    return out


def compile_images(line):
    """
    Convert ![alt](src) to <img src="src" alt="alt" />.
    Handles multiple images per line.
    """
    out = ''
    i = 0
    while i < len(line):
        if line.startswith('![', i):
            lb = i + 1
            rb = line.find(']', lb + 1)
            if rb == -1:
                out += line[i:]
                break

            if rb + 1 >= len(line) or line[rb + 1] != '(':
                out += line[i]
                i += 1
                continue

            rp = line.find(')', rb + 2)
            if rp == -1:
                out += line[i:]
                break

            alt = line[lb + 1:rb]
            src = line[rb + 2:rp]
            out += f'<img src="{src}" alt="{alt}" />'
            i = rp + 1
        else:
            out += line[i]
            i += 1
    return out

def compile_lines(lines):
    """
    Compile multiple lines of markdown into HTML.

    >>> compile_lines(["1. this", "2. is", "3. a", "4. list"])
    ['1. this 2. is 3. a 4. list']

    >>> compile_lines(["1. apple", "2. banana"])
    ['1. apple 2. banana']

    >>> compile_lines(["1. one"])
    ['1. one']
    """
    output = []
    buffer = []

    for line in lines:
        stripped = line.strip()

        # Check if line is a numbered list item (like "1. text")
        if (
            len(stripped) >= 3
            and stripped[0].isdigit()
            and stripped[1:3] == ". "
        ):
            buffer.append(stripped)
        else:
            # If we were collecting a list, flush it
            if buffer:
                output.append(" ".join(buffer))
                buffer = []

            output.append(line)

    # Flush remaining buffer
    if buffer:
        output.append(" ".join(buffer))

    return output
