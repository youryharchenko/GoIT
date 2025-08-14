from __future__ import annotations

from PySide6.QtWidgets import (
    QMainWindow
)

from hibiscus.node import Node
from hibiscus.project import Project

class GraphsNode(Node):
    def __init__(self, win: QMainWindow, project: Project):
        super().__init__("Graphs", win, project)