from __future__ import annotations
import logging
import sys
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
    Slot, Qt # Для вирівнювання або інших констант Qt
)

from hibiscus.project import Project

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

class MainWindow(QMainWindow):

    def __init__(self):
        logger.debug("MainWindow.__init__ started")
        super().__init__()

        self.setWindowTitle(f"Hibiscus - {last_project.name}")
        
        #self.setContentsMargins(40, 40, 40, 40)

        self.addToolBar(self._makeToolBar())
        self.setCentralWidget(self._makeCentral())

        apply_config(self)

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
        self.setWindowTitle(f"Hibiscus - {project.name}")
        self._apply_project()

    def _init_project(self, name):
        return Project({"name": name})
    
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
        
        tree.addTopLevelItem(QTreeWidgetItem(["DataFrames"]))
        tree.addTopLevelItem(QTreeWidgetItem(["Graphs"]))
        
      

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
        
        tree.header().sectionDoubleClicked.connect(on_header_double_clicked)
        
        return tree
    
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

    @Slot()
    def edit(self):
        logger.debug(f"Edit clicked")

    @Slot()
    def remove(self):
        logger.debug(f"Remove clicked")

    def closeEvent(self, event: QCloseEvent) -> None:
        try:
            set_config(self)
            logger.debug(f"MainWindow - closeEvent, config: {config}")

            with open(config_path, "wb") as f:
                pickle.dump(config, f)

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
    
    win = MainWindow() # Створюємо екземпляр головного вікна
    win.show() # Показуємо вікно
    ret = app.exec() # Запускаємо цикл подій

    logger.info(f"Finish. ret: {ret}")

    sys.exit(ret) 