from tree_sitter import Parser
from typing import List, Union

from taskHandling import Task, taskParser
from utils import get_parser

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

    def parserTaskLine(self, block: str) -> Union[Task, None]:
        return taskParser(block)

    def getTasks(self, oldTasks: Union[List[Task], None]) -> Union[List[Task], None]:
        out: List[Task] = []

        for block in self.code:
            if len(block) > 0:
                if 'TODO' in block:
                    out.append(self.parserTaskLine(block))

        out: List[Task] = list(
            filter(
                lambda x: x is not None,
                out
            )
        )

        if oldTasks is not None and len(out) > 0:
            out.extend(oldTasks)
            return list(set(out))

        elif oldTasks is None and len(out) > 0:
            return out

        elif oldTasks is not None and len(out) == 0:
            return

    def raw(self) -> List[str]:
        return self.code

    def __getitem__(self, idx: Union[int, slice]):
        return self.code[idx]

