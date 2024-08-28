from obsidianScripter import ObsidianIntegrationHandler
from analyzer import Analyzer
import argparse

class Main(Handler):
    def __init__(self, source_path: str, obsidian_vault_project_path: str, device: str) -> None:
        super().__init__(source_path, obsidian_vault_project_path, device)
        self.analyzer = Analyzer(source_path)
    def __call__(self) -> None:
        self.analyzer()
        for data in self.analyzer.last_data:
            self.next_TODO(data)

if __name__ == '__main__':
    # Parsing the arguments to the python parser
    parser = argparse.ArgumentParser(description="Parse and validate a path.")
    parser.add_argument('project_path', type=str, help="The path where the codebase is stored.")
    parser.add_argument('obsidian_vault_path', type=str, help="The obsidian vault path to save the preprocessed tasks.")
    parser.add_argument('device', type=str, help="LLM inference in which device.")
    args = parser.parse_args()
    # Creating the task
    Main(args.project_path, args.obsidian_vault_path, args.device)()

