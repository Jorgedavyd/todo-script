from typing import Callable, List
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import time

class ProjectObserver(FileSystemEventHandler):
    def __init__(self, project_path: str) -> None:
        self.history: List[str] = []
        self.path: str = project_path

    def on_modified(self, event):
        if not event.is_directory:
            self.history.append(event.src_path)
            print(f"File modified: {event.src_path}")

    def on_created(self, event):
        if not event.is_directory:
            self.history.append(event.src_path)
            print(f"File created: {event.src_path}")

    def on_deleted(self, event):
        if not event.is_directory:
            self.history.append(event.src_path)
            print(f"File deleted: {event.src_path}")

    def __call__(self, rutine: Callable) -> None:
        observer = Observer()
        observer.schedule(self, self.path, recursive = True)
        observer.start()

        print(f"Started watching {', '.join(self.path)}")

        try:
            while True:
                time.sleep(1)
                if self.changed_files:
                    changed_files = self.get_changed_files()
                    for filepath in changed_files:
                        rutine(filepath)
                    self.changed_files.clear()

        except KeyboardInterrupt:
            print('Job done.')

        observer.join()
