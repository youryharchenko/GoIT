from __future__ import annotations

import logging
import sys
import pickle
import pandas as pd


from PySide6.QtWidgets import (
    QMainWindow,
    QWidget,
    QVBoxLayout,
    QToolBar,
    QTableView,
    
    QInputDialog,
    QMessageBox
)

from PySide6.QtCore import (
    QModelIndex,
    QObject,
    QPersistentModelIndex,
    Qt,
    Slot, 
    Signal, 
    QAbstractTableModel
)

from PySide6.QtGui import (
    QAction, 
    QIcon
)

from hibiscus.node import Node
from hibiscus.project import Project

from hibiscus.project import Project, Data

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)


class DataFramesNode(Node):
    def __init__(self, win: QMainWindow, project: Project):
        super().__init__("DataFrames", win, project)

    def _makeDataItemNode(self):
        text, ok = QInputDialog.getText(self.treeWidget(), "New DataFrame", "DataFrame name:")
        if ok and text:
            logger.debug(f"DataFrame: {text}")
            return DataItemNode(text, self.win, self.project)
        else:
            return None
        
    def add(self):
        logger.debug(f"Node {self.get_text()} add")
        child = self._makeDataItemNode()
        if child:
            self.treeWidget().clearSelection()
            self.addChild(child)
            self.setExpanded(True)
            child.setSelected(True)
            if child.data_frame:
                self.project.add_data(child.data_frame)
        
class DataItemNode(Node):
    def __init__(self, name: str, win: QMainWindow, project: Project):
        super().__init__(name, win, project)
        self.data_frame = project.get_data_frame(name)
        if not self.data_frame:
            logger.error(f"Init DataItemNode: data '{name}' not found")
            self.data_frame = Data(name, 
                                   pd.DataFrame({"Column1": [], "Column2": [], "Column3": []}))
        else:
            logger.debug(f"Init DataItemNode: name: '{name}', data: {self.data_frame.data_frame} found")

    def edit(self):
        logger.debug(f"Node {self.get_text()} is edited")
        tabs = self._get_tab_widget()
        if tabs:
            title = f"{self.get_text()} - edit"
            for i in range(tabs.count()):
                if tabs.tabText(i) == title or tabs.tabText(i)[1:] == title:
                    tabs.setCurrentIndex(i)
                    return
            
            data_frame = self.data_frame.data_frame if self.data_frame else pd.DataFrame(
                {"Column1": [], "Column2": [], "Column3": []})
            editor = DataEditor(data_frame, tabs)
            i = tabs.addTab(editor, title)
            editor.set_index(i)

            editor.title_changed.connect(self.title_changed)
            editor.do_save.connect(self.do_save)
            tabs.setCurrentIndex(i)

    def rename(self):
        logger.debug(f"Node {self.get_text()} rename")
        old_name = self.get_text()
        data = self.project.get_data_frame(old_name)
        name, ok = QInputDialog.getText(self.treeWidget(), "Rename Node", "New Node name:", text=self.get_text())
        if data and ok and name:
            logger.debug(f"New Name: {name}")
            super().setText(0, name)
            data.name = name
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
    def do_save(self, data_frame: pd.DataFrame):
        logger.debug(f"Do save: {self.data_frame}")
        if self.data_frame is not None:
            self.data_frame.data_frame = data_frame

        try:
            with open(self.project.path, "wb") as f:
                pickle.dump(self.project.data, f)
        except Exception as e:
            logger.error(f"Save project error: {e}")
            QMessageBox.critical(self.treeWidget(), "Save project", f"{e}")
                    
class DataEditor(QWidget):

    title_changed = Signal(str, int)
    do_save = Signal(str) 

    def __init__(self, data_frame: pd.DataFrame, parent):
        super().__init__(parent)

        self.index = -1

        logger.debug(f"Data editor __init__: {data_frame}")
        self.data_frame = data_frame

        layout = QVBoxLayout(self)

        self.toolbar = QToolBar("WorkEditor Toolbar")

        self.save_action = QAction(QIcon.fromTheme("document-save"), "Save (Ctrl+s)", self) 
        self.save_action.triggered.connect(self.save)
        self.save_action.setEnabled(False)
        self.save_action.setShortcut("Ctrl+s")
        self.toolbar.addAction(self.save_action)

        # self.run_action = QAction(QIcon.fromTheme("media-playback-start"), "Run (Ctrl+r)", self) 
        # self.run_action.triggered.connect(self.run)
        # self.run_action.setEnabled(True)
        # self.run_action.setShortcut("Ctrl+r")
        # self.toolbar.addAction(self.run_action)
        
        layout.addWidget(self.toolbar)

        self.table = QTableView(parent=self)
        self.model = DataModel(data_frame)
        self.table.setModel(self.model)
                
        layout.addWidget(self.table)

    def set_index(self, index: int):
        self.index = index

    @Slot()
    def save(self):
        logger.debug(f"Save code")
        self.do_save.emit(self.data_frame)
        self.title_changed.emit("", self.index)
        #self.editor.document().setModified(False)

class DataModel(QAbstractTableModel):

    def __init__(self, data_frame: pd.DataFrame, parent = None ) -> None:
        super().__init__(parent)
        self.data_frame = data_frame

    def data(self, index, role=Qt.ItemDataRole.DisplayRole) :
        logger.debug(f"Data model data - index: {index}, role: {role}")

        if not index.isValid():
            return None

        if role == Qt.ItemDataRole.DisplayRole or role == Qt.ItemDataRole.EditRole:
            # Повертає значення з DataFrame для відображення або редагування
            return str(self.data_frame.iloc[index.row(), index.column()])

        return None
    
    def rowCount(self, parent=QModelIndex()) -> int:
        #logger.debug(f"Data model rowCount - parent: {parent}, rows: {self.data_frame.shape[0]}")
        return self.data_frame.shape[0]
    
    def columnCount(self, parent=QModelIndex()) -> int:
        #logger.debug(f"Data model columnCount - parent: {parent}, cols: {self.data_frame.shape[1]}")
        return self.data_frame.shape[1]
    
    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role == Qt.ItemDataRole.DisplayRole:
            if orientation == Qt.Orientation.Horizontal:
                # Заголовки стовпців
                return str(self.data_frame.columns[section])
            elif orientation == Qt.Orientation.Vertical:
                # Заголовки рядків
                return str(self.data_frame.index[section])
            
    def flags(self, index):
        # Вказує, що комірка може бути редагованою
        if not index.isValid():
            return Qt.ItemFlag.NoItemFlags
        return QAbstractTableModel.flags(self, index) | Qt.ItemFlag.ItemIsEditable
    
    def setData(self, index, value, role):
        # Метод для оновлення даних після редагування
        if not index.isValid():
            return False

        if role == Qt.ItemDataRole.EditRole:
            row = index.row()
            col = index.column()

            # Оновлюємо DataFrame
            self.data_frame.iloc[row, col] = value
            
            # Сповіщаємо view про зміну, щоб він оновився
            self.dataChanged.emit(index, index, [role])
            return True
        
        return False

