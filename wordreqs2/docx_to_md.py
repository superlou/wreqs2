import subprocess


def word_to_md(word_filename, md_filename):
    try:
        subprocess.run(['pandoc', word_filename,
                        '-o', md_filename,
                        '--markdown-headings=atx',
                        '--wrap=none',
                        '-f', 'docx+styles'])
    except FileNotFoundError as e:
        raise Exception('pandoc not found. Is pandoc 2.14 or later installed and in your path?')


def newline_after_meta(in_name, out_name):
    with open(in_name, 'r') as in_file:
        lines = in_file.readlines()

    with open(out_name, 'w') as out_file:
        for line in lines:
            if line[0:2] == '\\[':
                split_point = line.index('\\]') + 2
                # Write metadata
                out_file.write(line[0:split_point] + '\n')
                # Write requirement, removing leading space if it exists
                out_file.write(line[split_point:].strip() + '\n')
            else:
                out_file.write(line)
