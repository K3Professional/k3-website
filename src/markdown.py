"""A small Markdown-to-HTML converter for blog posts.

No outside packages, so the site builds anywhere Python runs (including
Netlify's build machines) without an install step that can fail.

Covers what the blog editor produces: headings, paragraphs, bold, italic,
links, images, bulleted and numbered lists, block quotes, tables, horizontal
rules, inline code, line breaks, and raw HTML blocks.
"""
import html
import re

_INLINE_TOKEN = re.compile(
    r"(!\[(?P<ialt>[^\]]*)\]\((?P<isrc>[^)\s]+)(?:\s+\"(?P<ititle>[^\"]*)\")?\))"
    r"|(\[(?P<ltext>[^\]]+)\]\((?P<lhref>[^)\s]+)(?:\s+\"(?P<ltitle>[^\"]*)\")?\))"
    r"|(`(?P<code>[^`]+)`)"
)


def _emphasis(text):
    text = re.sub(r"\*\*(.+?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"__(.+?)__", r"<strong>\1</strong>", text)
    text = re.sub(r"(?<![\w*])\*(?!\s)(.+?)(?<!\s)\*(?![\w*])", r"<em>\1</em>", text)
    text = re.sub(r"(?<![\w_])_(?!\s)(.+?)(?<!\s)_(?![\w_])", r"<em>\1</em>", text)
    return text


def inline(text):
    """Convert inline Markdown in one block of text to HTML."""
    out, pos = [], 0
    for m in _INLINE_TOKEN.finditer(text):
        out.append(_emphasis(html.escape(text[pos:m.start()], quote=False)))
        if m.group("isrc"):
            alt = html.escape(m.group("ialt"))
            out.append(f'<img src="{html.escape(m.group("isrc"))}" alt="{alt}" loading="lazy">')
        elif m.group("lhref"):
            href = m.group("lhref")
            external = href.startswith("http") and "k3professionalservices.com" not in href
            rel = ' target="_blank" rel="noopener"' if external else ""
            out.append(f'<a href="{html.escape(href)}"{rel}>{inline(m.group("ltext"))}</a>')
        else:
            out.append(f"<code>{html.escape(m.group('code'))}</code>")
        pos = m.end()
    out.append(_emphasis(html.escape(text[pos:], quote=False)))
    result = "".join(out)
    # Two trailing spaces or a backslash at a line end mean a line break.
    return re.sub(r"(?:  |\\)\n", "<br>\n", result)


def _split_row(line):
    line = line.strip().strip("|")
    return [c.strip() for c in line.split("|")]


def to_html(source):
    """Convert a whole Markdown document to HTML."""
    lines = source.replace("\r\n", "\n").split("\n")
    blocks, i = [], 0

    def para(buf):
        if buf:
            blocks.append(f"<p>{inline(chr(10).join(buf).strip())}</p>")

    buf = []
    while i < len(lines):
        line = lines[i]
        stripped = line.strip()

        if not stripped:
            para(buf); buf = []; i += 1
            continue

        # Raw HTML block: passed through untouched until a blank line.
        if stripped.startswith("<") and not buf:
            raw = []
            while i < len(lines) and lines[i].strip():
                raw.append(lines[i]); i += 1
            blocks.append("\n".join(raw))
            continue

        heading = re.match(r"^(#{1,6})\s+(.*?)\s*#*$", stripped)
        if heading:
            para(buf); buf = []
            level = max(2, len(heading.group(1)))  # the page title is the only <h1>
            blocks.append(f"<h{level}>{inline(heading.group(2))}</h{level}>")
            i += 1
            continue

        if re.match(r"^(\*\s*){3,}$|^(-\s*){3,}$|^(_\s*){3,}$", stripped):
            para(buf); buf = []
            blocks.append("<hr>")
            i += 1
            continue

        if stripped.startswith(">"):
            para(buf); buf = []
            quote = []
            while i < len(lines) and lines[i].strip().startswith(">"):
                quote.append(re.sub(r"^\s*>\s?", "", lines[i])); i += 1
            blocks.append(f"<blockquote>{to_html(chr(10).join(quote))}</blockquote>")
            continue

        # Table: a header row followed by a |---|---| separator row.
        if "|" in stripped and i + 1 < len(lines) and re.match(r"^\s*\|?\s*:?-{2,}", lines[i + 1]):
            para(buf); buf = []
            head = _split_row(lines[i]); i += 2
            rows = []
            while i < len(lines) and "|" in lines[i] and lines[i].strip():
                rows.append(_split_row(lines[i])); i += 1
            th = "".join(f"<th>{inline(c)}</th>" for c in head)
            body = "".join("<tr>" + "".join(f"<td>{inline(c)}</td>" for c in r) + "</tr>" for r in rows)
            blocks.append(f'<table class="compare"><thead><tr>{th}</tr></thead><tbody>{body}</tbody></table>')
            continue

        bullet = re.match(r"^\s*([-*+])\s+(.*)$", line)
        number = re.match(r"^\s*(\d+)[.)]\s+(.*)$", line)
        if (bullet or number) and not buf:
            ordered = bool(number)
            pattern = r"^\s*(\d+)[.)]\s+(.*)$" if ordered else r"^\s*([-*+])\s+(.*)$"
            items = []
            while i < len(lines):
                m = re.match(pattern, lines[i])
                if m:
                    items.append(m.group(2)); i += 1
                elif lines[i].startswith(("  ", "\t")) and lines[i].strip() and items:
                    items[-1] += " " + lines[i].strip(); i += 1
                else:
                    break
            tag = "ol" if ordered else "ul"
            blocks.append(f"<{tag}>" + "".join(f"<li>{inline(t)}</li>" for t in items) + f"</{tag}>")
            continue

        buf.append(line)
        i += 1

    para(buf)
    return "\n".join(blocks)
