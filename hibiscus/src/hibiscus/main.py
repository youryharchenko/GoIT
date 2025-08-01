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
    QTabWidget,
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

logger.debug(f"config: {config}")

class MainWindow(QMainWindow):

    def __init__(self):
        logger.debug("MainWindow.__init__ started")
        super().__init__()

        self.setWindowTitle("Hibiscus")
        
        #self.setContentsMargins(40, 40, 40, 40)

        self.addToolBar(self._makeToolBar())
        self.setCentralWidget(self._makeCentral())

        apply_config(self)

        logger.debug("MainWindow.__init__ finshed")

    def _makeToolBar(self) -> QToolBar:
        toolbar = QToolBar()

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
        return tree
    
    def _makeTabs(self, parent):
        tabs = QTabWidget(parent=parent)
        return tabs
    
    @Slot()
    def quit(self):
        self.close()

    def closeEvent(self, event: QCloseEvent) -> None:
        try:
            set_config(self)
            logger.debug(f"MainWindow - closeEvent, config: {config}")
            with open(config_path, "wb") as f:
                pickle.dump(config, f)
        except Exception as e:
            logger.error(f"Save config error: {e}")
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