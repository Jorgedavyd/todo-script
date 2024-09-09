from pygments.lexers import get_lexer_by_name
from tree_sitter import Language, Parser
from pygments.token import Comment
from typing import List, Dict, Set
import os.path as osp
import os

def get_comment(language: str) -> str:
    try:
        lexer = get_lexer_by_name(language)
        comment_tokens = [token for token, _ in lexer.get_tokens("") if token in Comment]
        if comment_tokens:
            return "".join(comment_tokens)
        else:
            return "//"
    except ValueError:
        return "//"


def get_filepaths(source_path: str) -> List[str]:
    filepaths = []
    for dirpath, _, filenames in os.walk(source_path):
        for filename in filenames:
            filepaths.append(osp.join(dirpath, filename))
    return filepaths


def get_language(filepath: str) -> str:
    extensions_to_languages: Dict[str, str] = {
        # Source code files
        '.py': 'python',
        '.cpp': 'cpp',
        '.hpp': 'cpp',
        '.c': 'c',
        '.h': 'c',
        '.java': 'java',
        '.js': 'javascript',
        '.ts': 'typescript',
        '.rb': 'ruby',
        '.go': 'go',
        '.php': 'php',
        '.swift': 'swift',
        '.kt': 'kotlin',
        '.rs': 'rust',
        '.html': 'html',
        '.css': 'css',
        '.json': 'json',
        '.yaml': 'yaml',
        '.md': 'markdown',
        '.r': 'r',
        '.m': 'objective-c',
        '.sql': 'sql',
        '.sh': 'bash',
        '.bat': 'batch',
        '.pl': 'perl',
        '.cu': 'cuda',
        '.cuh': 'cuda',
        '.cxx': 'cpp',
        '.cc': 'cpp',
        '.inl': 'cpp',
        '.tpp': 'cpp',
        '.def': 'c',
        '.tcl': 'tcl',
        '.toml': 'toml',
        '.ini': 'ini',
        '.conf': 'conf',
    }

    _, ext = osp.splitext(filepath)

    return extensions_to_languages.get(ext, 'text')

def get_languages(source_path: str) -> List[str]:
    out: Set[str] = set()
    for filepath in get_filepaths(source_path):
        out.add(get_language(filepath))
    return list(out)

def setup_parsers(project_path: str) -> None:
    name: str = osp.basename(project_path)
    Language.build_library(
        f'build/{name}.so',
        [f'tree-sitter-{language}' for language in get_languages(project_path)]
    )
def get_parser(language: str, project_name: str) -> Parser:
    name: str = osp.basename(project_name)
    input_language: Language = Language(f'build/{name}.so', language)
    parser: Parser = Parser()
    parser.set_language(input_language)
    return parser

