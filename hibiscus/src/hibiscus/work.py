from __future__ import annotations

import logging
import sys
import io
import builtins
import traceback
import pickle

from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QToolBar,
    QSplitter,
    QListWidget,
    QMainWindow,
    QInputDialog,
    QMessageBox
)

from PySide6.QtCore import (
    Slot, Qt, Signal # Для вирівнювання або інших констант Qt
)

from PySide6.QtGui import (
    QAction, 
    QIcon
)

from hibiscus.codeedit import WorkCodeEdit
from hibiscus.node import Node
from hibiscus.project import Project, Work

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

class WorksNode(Node):
    def __init__(self, win: QMainWindow, project: Project):
        super().__init__("Works", win, project)
        
    def _makeWorkItemNode(self):
        text, ok = QInputDialog.getText(self.treeWidget(), "New Work", "Work name:")
        if ok and text:
            logger.debug(f"Work: {text}")
            return WorkItemNode(text, self.win, self.project)
        else:
            return None
    
    def add(self):
        logger.debug(f"Node {self.get_text()} add")
        child = self._makeWorkItemNode()
        if child:
            self.treeWidget().clearSelection()
            self.addChild(child)
            self.setExpanded(True)
            child.setSelected(True)
            if child.work:
                self.project.add_work(child.work)

    
            



class WorkItemNode(Node):
    def __init__(self, name: str, win: QMainWindow, project: Project):
        super().__init__(name, win, project)
        self.work = project.get_work(name)
        if not self.work:
            logger.error(f"Init WorkItemNode: work '{name}' not found")
            self.work = Work(name, "")

    def run(self):
        logger.debug(f"Node {self.get_text()} is running")
        tabs = self._get_tab_widget()
        if tabs:
            title = f"{self.get_text()} - edit"
            for i in range(tabs.count()):
                if tabs.tabText(i) == title or tabs.tabText(i)[1:] == title:
                    tabs.setCurrentIndex(i)
                    editor = tabs.currentWidget()
                    if isinstance(editor, WorkEditor):
                        editor.run()
                    return
            
            code = self.work.code if self.work else ''
            editor = WorkEditor(code, tabs)
            i = tabs.addTab(editor, title)
            editor.set_index(i)
            
            editor.title_changed.connect(self.title_changed)
            editor.do_save.connect(self.do_save)
            tabs.setCurrentIndex(i)

            editor.run()

    def edit(self):
        logger.debug(f"Node {self.get_text()} is edited")
        tabs = self._get_tab_widget()
        if tabs:
            title = f"{self.get_text()} - edit"
            for i in range(tabs.count()):
                if tabs.tabText(i) == title or tabs.tabText(i)[1:] == title:
                    tabs.setCurrentIndex(i)
                    return
            
            code = self.work.code if self.work else ''
            editor = WorkEditor(code, tabs)
            i = tabs.addTab(editor, title)
            editor.set_index(i)

            editor.title_changed.connect(self.title_changed)
            editor.do_save.connect(self.do_save)
            tabs.setCurrentIndex(i)

    def rename(self):
        logger.debug(f"Node {self.get_text()} rename")
        old_name = self.get_text()
        work = self.project.get_work(old_name)
        name, ok = QInputDialog.getText(self.treeWidget(), "Rename Node", "New Node name:", text=self.get_text())
        if work and ok and name:
            logger.debug(f"New Name: {name}")
            super().setText(0, name)
            work.name = name
            tabs = self._get_tab_widget()
            if tabs:
                old_title = f"{old_name} - edit"
                for i in range(tabs.count()):
                    if tabs.tabText(i) == old_title or tabs.tabText(i)[1:] == old_title:

                        tabs.setTabText(i, tabs.tabText(i).replace(old_name, name, 1))
                        return


    @Slot()
    def title_changed(self, pref: str, index: int):
        tabs = self._get_tab_widget()
        if tabs:
            tabs.setTabText(index, f"{pref}{self.get_text()} - edit")

    @Slot()
    def do_save(self, text: str):
        logger.debug(f"Do save: {self.work}, text: {text}")
        if self.work:
            self.work.code = text

        try:
            with open(self.project.path, "wb") as f:
                pickle.dump(self.project.data, f)
        except Exception as e:
            logger.error(f"Save project error: {e}")
            QMessageBox.critical(self.treeWidget(), "Save project", f"{e}")
        

    

class WorkEditor(QWidget):

    title_changed = Signal(str, int)
    do_save = Signal(str) 

    def __init__(self, text: str, parent):
        super().__init__(parent)

        self.run_globals = {}
        self.run_locals = {} 

        self.index = -1

        layout = QVBoxLayout(self)

        self.toolbar = QToolBar("WorkEditor Toolbar")

        self.save_action = QAction(QIcon.fromTheme("document-save"), "Save (Ctrl+s)", self) 
        self.save_action.triggered.connect(self.save)
        self.save_action.setEnabled(False)
        self.save_action.setShortcut("Ctrl+s")
        self.toolbar.addAction(self.save_action)

        self.run_action = QAction(QIcon.fromTheme("media-playback-start"), "Run (Ctrl+r)", self) 
        self.run_action.triggered.connect(self.run)
        self.run_action.setEnabled(True)
        self.run_action.setShortcut("Ctrl+r")
        self.toolbar.addAction(self.run_action)
        
        layout.addWidget(self.toolbar)

        splitter = QSplitter(parent=self, orientation=Qt.Orientation.Vertical)


        self.editor = WorkCodeEdit(text)
        self.editor.dirty_changed.connect(self.dirty_changed)
        #self.editor.text_saved.connect(self.text_saved)

        splitter.addWidget(self.editor)


        self.output = QListWidget(parent=splitter)

        splitter.addWidget(self.output)
        
        layout.addWidget(splitter)

    def set_index(self, index: int):
        self.index = index

    @Slot()
    def save(self):
        logger.debug(f"Save code")
        self.do_save.emit(self.editor.toPlainText())
        self.title_changed.emit("", self.index)
        self.editor.document().setModified(False)

    @Slot()
    def run(self):
        logger.debug(f"Run code")

        self.output.clear()

        self.run_globals["__builtins__"] = builtins

        old_stdout = sys.stdout
        old_stderr = sys.stderr

        redirected_output = io.StringIO()
        
        sys.stdout = redirected_output
        sys.stderr = redirected_output

        try:
            # print("Вміст self.run_globals перед exec():")
            # for key, value in self.run_globals.items():
            #     print(f"  {key}: {type(value)}")

            exec(self.editor.toPlainText(), self.run_globals)
        except Exception as e:
            #self.output.addItem(f"Error: {e.with_traceback()}")
            traceback.print_exception(e)
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr
            output_content = redirected_output.getvalue()
            if output_content:
                for item in output_content.strip().split("\n"):
                    self.output.addItem(item)
        

    @Slot()
    def dirty_changed(self, state: bool):
        logger.debug(f"Dirty changed: state = {state}")
        if state:
            pref = "*"
            self.save_action.setEnabled(True)
        else:
            pref = "" 
            self.save_action.setEnabled(False)
        self.title_changed.emit(pref, self.index)
        #self.changed = state

    # @Slot()
    # def text_saved(self, text: str):
    #     logger.debug(f"Text saved: state = {text}")
        


