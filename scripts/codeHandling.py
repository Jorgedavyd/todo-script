from utils import get_language, get_parser
from definitions import VALID_PRIORITY
from tree_sitter import Parser
from taskHandling import Task
from datetime import datetime
from typing import Dict, List
import re

class Code:
    code: List[str] = []

    def __init__(self, filepath: str, language: str, project_name: str) -> None:
        self.path: str = filepath
        self.language: str = language
        self.parser: Parser = get_parser(language, project_name)
        self.renderFile()

    def renderFile(self) -> None:
        with open(self.path, 'r') as file:
            code = file.read()

        ast = self.parser.parse(bytes(code, 'utf-8'))

        def traverse(node):
            if node.type in ['class_definition', 'function_definition']:
                self.code.append(node.text.decode('utf8'))
            elif node.type not in ['comment', 'string']:
                if not any(child.type in ['class_definition', 'function_definition'] for child in node.children):
                    self.code.append(node.text.decode('utf8'))

            for child in node.children:
                traverse(child)

        traverse(ast.root_node)

    def append(self, code: List[str]) -> None:
        self.code.extend(code)

    def parserTaskLine(self, block: str, idx: int, path: str) -> Dict[str, str | int]:
        pattern = r"TODO\s+(\d{2}\d{2}\d{2})\s+([A-Z])\s+(.*)"
        match = re.match(pattern, block)

        if match:
            date_str = match.group(1)
            priority = match.group(2).lower()
            description = match.group(3)

            if priority not in VALID_PRIORITY:
                raise ValueError(f'Invalid priority: {priority}, expected: {VALID_PRIORITY}')

            date_format = datetime.strptime(date_str, "%d%m%y").date()

            return Task(**{
                "line": idx,
                "date": date_format.isoformat(),
                "priority": priority,
                "description": description,
                "context": block
            })

        else:
            raise ValueError('Not valid input query, TODO pattern doesn\'t match the expected one: TODO <date:%d%m%y> <priority> <description>')
    def getTasks(self) -> List[Task] | None:
        out: List[Task] = []

        for block in self.code:
            if 'TODO' in block:
                self.parserTaskLine(block)

        return out if len(out) > 0 else None

    def raw(self) -> List[str]:
        return self.code

    def __getitem__(self, idx: int | slice):
        return self.code[idx]

