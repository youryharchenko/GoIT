from __future__ import annotations
import logging
import sys

from PySide6.QtWidgets import (
    QTreeWidgetItem,
    QSplitter,
    QTabWidget,
    QMessageBox,
    QMainWindow
)

from hibiscus.project import Project

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)


class Node(QTreeWidgetItem):
    def __init__(self, text: str, win: QMainWindow, project: Project):
        super().__init__([text])
        self.win = win
        self.project = project

    def _get_tab_widget(self):
        
        central = self.win.centralWidget()
        if not isinstance(central, QSplitter):
            logger.error(f"Central must be QSplitter, it is {type(central) }")
            return None
        
        tabs = central.widget(1)
        if not isinstance(tabs, QTabWidget):
            logger.error(f"Left must be QTabWidget, it is {type(tabs) }")
            return None
        
        return tabs

    def get_text(self) -> str:
        return(super().text(0))
    
    def run(self):
        logger.warning(f"Node {self.get_text()} can not run")
        QMessageBox.warning(self.treeWidget(), self.get_text(), 
                    f"Node {self.get_text()} can not be ran")

    def add(self):
        logger.warning(f"Node {self.get_text()} can not add")
        QMessageBox.warning(self.treeWidget(), self.get_text(), 
                    f"Node {self.get_text()} can not be added")

    def edit(self):
        logger.warning(f"Node {self.get_text()} can not be edited")
        QMessageBox.warning(self.treeWidget(), self.get_text(), 
                    f"Node {self.get_text()} can not be edited")

    def rename(self):
        logger.warning(f"Node {self.get_text()} can not be renamed")
        QMessageBox.warning(self.treeWidget(), self.get_text(), 
                    f"Node {self.get_text()} can not be renamed")
   