from __future__ import annotations
import logging
import sys
import io
import pathlib
import pickle

from appdirs import user_data_dir

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QToolBar,
    QSplitter,
    QTreeWidget,
    QTreeWidgetItem,
    QTabWidget,
    QInputDialog,
    QFileDialog,
    QVBoxLayout,
    QListWidget,
    QTextEdit,
    #QStatusBar,
    QWidget,
    QGridLayout,
    #QVBoxLayout,
    #QLabel, # Приклад вашого "розробленого віджета" або його вмісту
    QPushButton, # Приклад додавання кнопки до тулбара
    QComboBox,
    QSizePolicy
)

from PySide6.QtGui import (
    QAction, QCloseEvent, QIcon, QMoveEvent, QPixmap, QResizeEvent # Для дій та іконок в тулбарі
)

from PySide6.QtCore import (
    Slot, Qt, Signal # Для вирівнювання або інших констант Qt
)

from hibiscus.project import Project, Work
from hibiscus.codeedit import WorkCodeEdit

app_name = "Hibiscus"
app_author = "YouryHarchenko"

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
if not logger.handlers:
    handler = logging.StreamHandler(sys.stderr)

    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    logger.addHandler(handler)

data_path = pathlib.Path(user_data_dir(app_name, app_author))
if not data_path.exists():
    data_path.mkdir(parents=True, exist_ok=True)
elif not data_path.is_dir():
    logger.fatal(f"Path {data_path} is not dir!")
    sys.exit(1)

logger.debug(f"User dir: {data_path}")


config_path = data_path.joinpath(".config")
try:
    with open(config_path, "rb") as f:
        config = pickle.load(f)
except Exception as e:
    logger.warning(f"Load config error: {e}, create new")
    config = {}

project_path = data_path.joinpath("projects")
if not project_path.exists():
    project_path.mkdir(parents=True, exist_ok=True)
elif not data_path.is_dir():
    logger.fatal(f"Path {project_path} is not dir!")
    sys.exit(1)

logger.debug(f"Projects dir: {project_path}")
last_project = config.get("last-project", "")
project = Project({"name": pathlib.Path(last_project).name})

logger.debug(f"config: {config}")

class Node(QTreeWidgetItem):
    def __init__(self, text: str):
        super().__init__([text])

    def _get_tab_widget(self):
        
        central = win.centralWidget()
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

    def add(self):
        logger.warning(f"Node {self.get_text()} can not add")

    def edit(self):
        logger.warning(f"Node {self.get_text()} can not be edited")

    def rename(self):
        logger.warning(f"Node {self.get_text()} can not be renamed")
   

class WorksNode(Node):
    def __init__(self):
        super().__init__("Works")

    def _makeWorkItemNode(self):
        text, ok = QInputDialog.getText(self.treeWidget(), "New Work", "Work name:")
        if ok and text:
            logger.debug(f"Work: {text}")
            return WorkItemNode(text)
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
                project.add_work(child.work)

    
            



class WorkItemNode(Node):
    def __init__(self, name: str):
        super().__init__(name)
        self.work = project.get_work(name)
        if not self.work:
            logger.error(f"Init WorkItemNode: work '{name}' not found")
            self.work = Work(name, "")

    def run(self):
        logger.debug(f"Node {self.get_text()} is running")

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
        work = project.get_work(old_name)
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
        

    

class DataFramesNode(Node):
    def __init__(self):
        super().__init__("DataFrames")

class GraphsNode(Node):
    def __init__(self):
        super().__init__("Graphs")

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

        old_stdout = sys.stdout
        old_stderr = sys.stderr

        redirected_output = io.StringIO()
        
        sys.stdout = redirected_output
        sys.stderr = redirected_output

        try:
            exec(self.editor.toPlainText(), self.run_globals, self.run_locals)
        except Exception as e:
            self.output.addItem(f"Error: {e}")
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
        





class MainWindow(QMainWindow):

    def __init__(self):
        logger.debug("MainWindow.__init__ started")
        super().__init__()

        self.setWindowTitle(f"Hibiscus - {last_project.name}")
        
        #self.setContentsMargins(40, 40, 40, 40)

        self.addToolBar(self._makeToolBar())
        self.setCentralWidget(self._makeCentral())

        apply_config(self)

        self.open_project(project.name)
        self._apply_project()

        logger.debug("MainWindow.__init__ finshed")

    def new_project(self, name: str):
        global last_project
        global project
        last_project = project_path.joinpath(name)
        config["last-project"] = last_project
        project = self._init_project(name)
        self.setWindowTitle(f"Hibiscus - {project.name}")
        self._apply_project()

    def open_project(self, name):
        global last_project
        global project
        last_project = project_path.joinpath(name)
        config["last-project"] = last_project
        try:
            with open(last_project, "rb") as f:
                project = Project(pickle.load(f))
        except Exception as e:
            logger.warning(f"Load project error: {e}, create new")
            project = self._init_project(name)

        logger.debug(f"Open Project data: {project.data}")
        self.setWindowTitle(f"Hibiscus - {project.name}")
        self._apply_project()

    def _init_project(self, name):
        return Project({"name": name, "works": []})
    
    def _apply_project(self):
        central = self.centralWidget()
        if not isinstance(central, QSplitter):
            logger.error(f"Central must be QSplitter, it is {type(central) }")
            return
        tree = central.widget(0)
        if not isinstance(tree, QTreeWidget):
            logger.error(f"Left must be QTreeWidget, it is {type(tree) }")
            return
        tabs = central.widget(1)
        if not isinstance(tabs, QTabWidget):
            logger.error(f"Left must be QTabWidget, it is {type(tabs) }")
            return
                
        tree.clear()
        
        tree.setHeaderLabels([project.name])
        
        works_node = WorksNode()
        for work in project.works:
            works_node.addChild(WorkItemNode(work.name))
        tree.addTopLevelItem(works_node)

        tree.addTopLevelItem(DataFramesNode())
        tree.addTopLevelItem(GraphsNode())
        
      

    def _makeToolBar(self) -> QToolBar:
        toolbar = QToolBar()

        new_action = QAction(QIcon.fromTheme("document-new"), "New", self) 
        new_action.triggered.connect(self.new)
        toolbar.addAction(new_action)

        open_action = QAction(QIcon.fromTheme("document-open"), "Open", self) 
        open_action.triggered.connect(self.open)
        toolbar.addAction(open_action)

        toolbar.addSeparator()

        add_action = QAction(QIcon.fromTheme("list-add"), "Add", self) 
        add_action.triggered.connect(self.add)
        toolbar.addAction(add_action)

        edit_action = QAction(QIcon.fromTheme("document-properties"), "Edit", self) 
        edit_action.triggered.connect(self.edit)
        toolbar.addAction(edit_action)

        remove_action = QAction(QIcon.fromTheme("list-remove"), "Remove", self) 
        remove_action.triggered.connect(self.remove)
        toolbar.addAction(remove_action)

        toolbar.addSeparator()

        run_action = QAction(QIcon.fromTheme("media-playback-start"), "Run", self) 
        run_action.triggered.connect(self.run)
        toolbar.addAction(run_action)

        toolbar.addSeparator()

        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        toolbar.addWidget(spacer)

        exit_action = QAction(QIcon.fromTheme("application-exit"), "Quit", self) # Можна додати іконку
        exit_action.triggered.connect(self.quit) # Зв'язуємо дію із закриттям вікна
        toolbar.addAction(exit_action)

        return toolbar
    
    def _makeCentral(self):
        widget = QSplitter(parent=self, orientation=Qt.Orientation.Horizontal)
               
        widget.addWidget(self._makeTree(widget))
        widget.addWidget(self._makeTabs(widget))

        return widget
    
    def _makeTree(self, parent):
        tree = QTreeWidget(parent=parent, columnCount=1)
        tree.setSelectionMode(QTreeWidget.SelectionMode.SingleSelection)

        def on_header_double_clicked():
            logger.debug(f"Tree header double clicked")
            name, ok = QInputDialog.getText(self, "Rename Project", "New Project name:", text=project.name)
            if ok and name:
                logger.debug(f"Name: {name}")
                global last_project
                last_project = project_path.joinpath(name)
                config["last-project"] = last_project
                project.set_name(name)
                self.setWindowTitle(f"Hibiscus - {project.name}")
                tree.setHeaderLabels([project.name])

        def on_item_double_clicked(item: Node, _):
            logger.debug(f"Tree item double clicked: {item.get_text()}")    
            item.rename()

        
        tree.header().sectionDoubleClicked.connect(on_header_double_clicked)
        tree.itemDoubleClicked.connect(on_item_double_clicked)
        
        return tree
    
    def _get_selected_tree_item(self):
        central = self.centralWidget() 
        if not isinstance(central, QSplitter):
            logger.error(f"Central must be QSplitter, it is {type(central) }")
            return None
        
        tree = central.widget(0)
        if not isinstance(tree, QTreeWidget):
            logger.error(f"Left must be QTreeWidget, it is {type(tree) }")
            return None
        
        items = tree.selectedItems()
        if len(items) > 0:
            return items[0]
        
        return None


    
    def _makeTabs(self, parent):
        tabs = QTabWidget(parent=parent)
        return tabs
    
    @Slot()
    def quit(self):
        self.close()

    @Slot()
    def new(self):
        logger.debug(f"New clicked")
        text, ok = QInputDialog.getText(self, "New Project", "Project name:")
        if ok and text:
            logger.debug(f"Name: {text}")
            self.new_project(text)

    @Slot()
    def open(self):
        logger.debug(f"Open clicked")
        name, filter = QFileDialog.getOpenFileName(self, "Open Project", str(project_path))
        logger.debug(f"Name: {name}, filter: {filter}")
        
        self.open_project(name)

    @Slot()
    def add(self):
        logger.debug(f"Add clicked")
        node = self._get_selected_tree_item()
        if node and isinstance(node, Node):
            logger.debug(f"Selected item: {node.get_text()}")
            node.add()

    @Slot()
    def edit(self):
        logger.debug(f"Edit clicked")
        node = self._get_selected_tree_item()
        if node and isinstance(node, Node):
            logger.debug(f"Selected item: {node.get_text()}")
            node.edit()

    @Slot()
    def remove(self):
        logger.debug(f"Remove clicked")

    @Slot()
    def run(self):
        logger.debug(f"Run clicked")
        node = self._get_selected_tree_item()
        if node and isinstance(node, Node):
            logger.debug(f"Selected item: {node.get_text()}")
            node.run()


    def closeEvent(self, event: QCloseEvent) -> None:
        try:
            set_config(self)
            logger.debug(f"MainWindow - closeEvent, config: {config}")
            with open(config_path, "wb") as f:
                pickle.dump(config, f)

            logger.debug(f"Save Project data: {project.data}")
            with open(last_project, "wb") as f:
                pickle.dump(project.data, f)

        except Exception as e:
            logger.error(f"Save error: {e}")
        return super().closeEvent(event)
    
    def resizeEvent(self, event: QResizeEvent) -> None:
        size = event.size()
        config["main-width"] = size.width()
        config["main-height"] = size.height()
        return super().resizeEvent(event)
    
    def moveEvent(self, event: QMoveEvent) -> None:
        pos = event.pos()
        config["main-x"] = pos.x()
        config["main-y"] = pos.y()
        return super().moveEvent(event)
    

def set_config(win: MainWindow):
    central = win.centralWidget() 
    sizes = central.sizes() if isinstance(central, QSplitter) else [win.width() // 3, win.width() - (win.width() // 3)]
    config["tree-size"] = sizes[0]
    config["tabs-size"] = sizes[1]

def apply_config(win: MainWindow):
    win.setGeometry(
        int(config.get("main-x", 100)), 
        int(config.get("main-y", 100)), 
        int(config.get("main-width", 1024)),
        int(config.get("main-height", 800)))
    
    central = win.centralWidget() 
    if isinstance(central, QSplitter):
        central.setSizes([config.get("tree-size", win.width() // 3), config.get("tabs-size", (win.width() - win.width() // 3))])
    

        

def main():
    logger.info(f"Start. argv: {sys.argv}")

    app = QApplication(sys.argv) # Передаємо аргументи командного рядка
    
    global win
    win = MainWindow() # Створюємо екземпляр головного вікна
    win.show() # Показуємо вікно
    ret = app.exec() # Запускаємо цикл подій

    logger.info(f"Finish. ret: {ret}")

    sys.exit(ret) 