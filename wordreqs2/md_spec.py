from enum import Enum
from dataclasses import dataclass
import re
from .util import flatten


class Spec():
    def __init__(self):
        self.blocks = []
        self.filename = None

    def add_block(self, block):
        self.blocks.append(block)

    @property
    def reqs(self):
        return [block for block in self.blocks if isinstance(block, Req)]

    @property
    def mod_signals(self):
        return set(flatten([req.mod_signals for req in self.reqs]))

    @property
    def signals(self):
        return set(flatten([req.signals for req in self.reqs]))
    
    def get_req(self, req_id) -> "Req":
        found = [req for req in self.reqs if req.id == req_id]
        
        if len(found) == 0:
            raise IndexError("No req found!")
        elif len(found) > 1:
            raise IndexError("More than 1 req found for this ID!")
        
        return found[0]


class Heading():
    def __init__(self, line: str):
        self.md = line
        self.level = line.split(' ')[0].count('#')
        self.content = line.replace('#', '').strip()


@dataclass
class Req():
    id: str
    content: str
    req_trace_ids: list[str]
    raw_metadata: str

    CUSTOM_STYLE_PATTERN = r'\[([\w: ]+)]\{custom-style="([\w ]+)"\}'

    def __init__(self, meta_line: str):
        self.raw_metadata = meta_line
        line = meta_line.replace(r'\[', '[')
        line = line.replace(r'\]', ']')
        topics = line.split(']')

        req_topic = topics[0]
        req_topic = req_topic.replace('[', '')

        if '→' in req_topic:
            req_id, req_trace_ids = req_topic.split('→')
            self.req_trace_ids = [id.strip()
                                  for id in req_trace_ids.split(',')
                                  if id.strip() != '']
        elif '\\>' in req_topic:
            req_id, req_trace_ids = req_topic.split('\\>')
            self.req_trace_ids = [id.strip()
                                  for id in req_trace_ids.split(',')
                                  if id.strip() != '']                                  
        else:
            req_id = req_topic
            self.req_trace_ids = []

        self.id = req_id.strip()
        self.content = ""

    def add_content_line(self, line: str):
        self.content += line

    @property
    def signals(self):
        matches = re.findall(Req.CUSTOM_STYLE_PATTERN, self.content)
        signals = [match[0] for match in matches
                   if 'Signal' in match[1].split(' ')]
        signals = set(signals)  # Keep unique
        return signals
    
    @property
    def mod_signals(self):
        matches = re.findall(Req.CUSTOM_STYLE_PATTERN, self.content)
        signals = [match[0] for match in matches
                   if 'ModSignal' in match[1].split(' ')]
        signals = set(signals)  # Keep unique
        return signals


def is_heading(line: str):
    return len(line) >= 1 and line[0] == '#'


def is_req_meta(line: str):
    return len(line) >= 2 and line[0:2] == r'\['


def is_blank(line: str):
    return line.strip() == ''


def is_end(line: str):
    return line == '<EOT>'


class ParseState(Enum):
    NONE = 0
    HEADING = 1
    REQ_META = 2
    REQ = 3
    END = 4


def parse_file(filename):
    with open(filename, encoding='utf8') as md_file:
        spec = parse_lines(md_file.readlines())
        spec.filename = filename
        return spec


def parse_lines(lines):
    lines += ['<EOT>']
    lines = remove_fenced_styles(lines)
    spec = Spec()
    state = ParseState.NONE

    current_req = None

    for i, line in enumerate(lines):
        # Update state
        if state == ParseState.NONE:
            if is_req_meta(line):
                state = ParseState.REQ_META
            elif is_heading(line):
                state = ParseState.HEADING
            elif is_end(line):
                state = ParseState.END
            else:
                state = ParseState.NONE
        elif state == ParseState.HEADING:
            if is_blank(line):
                state = ParseState.NONE
            if is_heading(line):
                state = ParseState.HEADING
            elif is_end(line):
                state = ParseState.END
            else:
                state = ParseState.NONE
        elif state == ParseState.REQ_META:
            if is_heading(line):
                state = ParseState.HEADING
            elif is_req_meta(line):
                state = ParseState.REQ_META
            elif is_end(line):
                state = ParseState.END
            else:
                state = ParseState.REQ
        elif state == ParseState.REQ:
            if is_heading(line):
                state = ParseState.HEADING
            elif is_req_meta(line) and is_blank(lines[i - 1]):
                # A blank line must preceed the start of a new requirement
                state = ParseState.REQ_META
            elif is_end(line):
                state = ParseState.END
            else:
                state = ParseState.REQ

        # Process line
        if state != ParseState.REQ and current_req:
            current_req.content = current_req.content.strip()
            spec.add_block(current_req)
            current_req = None

        if state == ParseState.HEADING:
            spec.add_block(Heading(line))
        elif state == ParseState.REQ_META:
            current_req = Req(line)
        elif state == ParseState.REQ:
            current_req.add_content_line(line)

    return spec


def remove_fenced_styles(lines):
    lines = [line for line in lines if line[0:3] != ':::']
    return lines
