from typing import Callable


class Command:
    def __init__(self, name: str, handler: Callable, description: str):
        self.name = name
        self.handler = handler
        self.description = description

    def __str__(self):
        return f"Command '{self.name}': {self.description}"

    def execute(self, *args, **kwargs):
        return self.handler(*args, **kwargs)









