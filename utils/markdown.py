import os
from tempfile import NamedTemporaryFile

def convert_markdown (html_source):
    with NamedTemporaryFile() as html_file:
        with NamedTemporaryFile() as md_file:
            html_file.write (html_source)
            html_file.flush()

            cmd_parts = ["pandoc", "--from=html", "--to=markdown_github", html_file.name, "-o", md_file.name]
            cmd = " ".join(cmd_parts)
            res = os.system(cmd)
            markdown = md_file.read()
            return markdown
