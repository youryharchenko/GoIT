from __future__ import annotations
import logging
import sys
import os
from pathlib import Path
#import random
from typing import List
from gomoku.game import Game

from PySide6.QtWidgets import (
    QApplication,
    QMainWindow,
    QToolBar,
    #QStatusBar,
    QWidget,
    QGridLayout,
    #QVBoxLayout,
    #QLabel, # Приклад вашого "розробленого віджета" або його вмісту
    QPushButton, # Приклад додавання кнопки до тулбара
    QComboBox,
    QSizePolicy
)
from PySide6.QtGui import QAction, QIcon, QPixmap # Для дій та іконок в тулбарі
from PySide6.QtCore import Slot, Qt # Для вирівнювання або інших констант Qt

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Щоб повідомлення виводилися на консоль, потрібно додати обробник (handler)
# Перевіряємо, чи вже є обробники, щоб уникнути дублювання виводу при повторному імпорті модуля
if not logger.handlers:
    # Створюємо обробник для виводу на стандартний потік помилок (консоль)
    handler = logging.StreamHandler(sys.stderr)

    # (Опціонально) Встановлюємо рівень для обробника (зазвичай такий самий, як у логера, або нижчий)
    #handler.setLevel(logging.DEBUG)

    # (Опціонально) Встановлюємо формат виводу повідомлень
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    handler.setFormatter(formatter)

    # Додаємо обробник до логера
    logger.addHandler(handler)

class Desk(QWidget):
    def __init__(self, n: int, game: Game, parent: MainWindow | None = None):
        """
        Ініціалізує GridWidget.

        Args:
            n (int): Розмір решітки (n x n).
            parent (QWidget, optional): Батьківський віджет. За замовчуванням None.
        """

        logger.debug("Desk.__init__ started")

        self.main = parent

        super().__init__(parent)
        self.setAttribute(Qt.WidgetAttribute.WA_StyledBackground, True) 
        
        if n <= 0:
            raise ValueError("Розмір решітки 'n' має бути більше нуля.")
        
        self.setObjectName("Desk")
        self.setStyleSheet("""
            #Desk {
                border: 2px solid black;
                background-color: lightgray;
            }
        """)
        self.setContentsMargins(10, 10, 10, 10)

        # Шлях до директорії поточного скрипта
        current_dir = Path(__file__).parent

        # Створюємо QIcon. Можна завантажити з файла або з ресурсів.
        # Приклад завантаження з файла:
        image_path: str = os.path.join(current_dir, 'assets', 'img', 'Empty.png')
        pixmap_empty = QPixmap(image_path)
        self.icon_empty = QIcon(pixmap_empty)

        image_path: str = os.path.join(current_dir, 'assets', 'img', 'Black.png')
        pixmap_black = QPixmap(image_path)
        icon_black = QIcon(pixmap_black)

        image_path: str = os.path.join(current_dir, 'assets', 'img', 'White.png')
        pixmap_white = QPixmap(image_path)
        icon_white = QIcon(pixmap_white)

        self.icon_colors: List[QIcon] = [icon_black, icon_white]

        style = "{padding: 0px; border: none; margin: 0px; background-color: red;}"

        

        self.grid_size = n
        #self.widget_type = widget_type
        self._widgets: List[List[QPushButton]] = [] # Список для зберігання посилань на створені віджети

        # Створюємо менеджер компонування QGridLayout
        grid_layout = QGridLayout(self)
        grid_layout.setSpacing(0) # Можна встановити відступи між віджетами
        grid_layout.setHorizontalSpacing(0)
        grid_layout.setVerticalSpacing(0)
        grid_layout.setContentsMargins(0, 0, 0, 0)
    
        
        # Створюємо та додаємо віджети до решітки
        for row in range(n):
            row_widgets: List[QPushButton] = [] # Список для віджетів у поточному рядку
            for col in range(n):
                # Створюємо екземпляр віджета вказаного типу
                widget = QPushButton()
                obj_name = f"Pos_{row}_{col}"
                widget.setObjectName(obj_name)
                widget.setStyleSheet(f"#{obj_name} {style}")
                widget.setIcon(self.icon_empty)
                widget.setIconSize(pixmap_empty.size())
                widget.setFixedSize(pixmap_empty.size())
                widget.setToolTip(f"{row},{col}")
                widget.adjustSize()
                
                # Підключення сигналу, якщо потрібно
                widget.clicked.connect(lambda st=False, r=row, c=col: self.on_button_clicked(r, c))

                # Додаємо віджет до QGridLayout за вказаними рядком та стовпцем
                grid_layout.addWidget(widget, row, col)
                row_widgets.append(widget) # Зберігаємо посилання на віджет

            self._widgets.append(row_widgets) # Додаємо рядок віджетів до загального списку

        # Встановлюємо QGridLayout як основний компонувальник для GridWidget
        self.setLayout(grid_layout)

        self.game = game

        logger.debug("Desk.__init__ finished")

    # Приклад методу для доступу до окремого віджета
    def get_widget_at(self, row: int, col: int) -> QPushButton | None:
        if 0 <= row < self.grid_size and 0 <= col < self.grid_size:
            return self._widgets[row][col]
        return None
        
    # Приклад обробника сигналу для кнопок (якщо widget_type=QPushButton)
    @Slot(int, int)
    def on_button_clicked(self, row: int, col: int):
        logger.debug(f"Натиснуто кнопку в позиції ({row}, {col})")
        # Додайте вашу логіку обробки натискання кнопки тут
        if self.game.is_play and not self.game.is_run and not self.game.is_busy:
            y, x = row, col
            if self.game.net.get_point(x, y).s == 0 and isinstance(self.main, MainWindow):
                logger.debug(f"Manual step: {x}, {y}")
                self.main.go(False, x, y)


    def init(self):

        logger.debug("Desk.init started")

        for row in range(self.grid_size):
            for col in range(self.grid_size):
                widget = self.get_widget_at(row, col)
                if isinstance(widget, QPushButton):
                    widget.setIcon(self.icon_empty)

        logger.debug("Desk.init finshed")

    def draw_step(self, x: int, y: int, c: int):
        logger.debug(f"Desk.draw_step({x}, {y}, {c}) started")
        widget = self.get_widget_at(y, x)
        if isinstance(widget, QPushButton):
            widget.setIcon(self.icon_colors[c])
        logger.debug(f"Desk.draw_step({x}, {y}, {c}) finished")

class Step:
    def __init__(self, x: int, y: int, msg: str):
        self.x = x
        self.y = y
        self.msg = msg


class MainWindow(QMainWindow):
    def __init__(self):

        logger.debug("MainWindow.__init__ started")

        super().__init__()

        self.n = 15

        self.setWindowTitle("Gomoku in Python")
        self.setGeometry(100, 100, 600, 800)
        self.setContentsMargins(40, 0, 40, 0)

        # 1. Створення та встановлення центрального віджета
        self.game = Game(self.n)
        self.desk = Desk(self.n, self.game, self) # Створюємо екземпляр вашого віджета
        
        self.setCentralWidget(self.desk) # Встановлюємо його як центральний

        # 2. Створення та налаштування тулбара
        toolbar = QToolBar("Основний тулбар")
        self.addToolBar(toolbar) # Додаємо тулбар до головного вікна
        
        self.new_action = QAction("New", self) # Можна додати іконку
        self.new_action.triggered.connect(self.new) # Зв'язуємо дію із закриттям вікна
        toolbar.addAction(self.new_action)
        
        self.mode_box = QComboBox()
        self.mode_box.addItem("Black")
        self.mode_box.addItem("White")
        self.mode_box.addItem("Manual")
        self.mode_box.setCurrentText("Black")
        toolbar.addWidget(self.mode_box)

        self.step_action = QAction("Step", self) # Можна додати іконку
        self.step_action.triggered.connect(self.step) # Зв'язуємо дію із закриттям вікна
        self.step_action.setDisabled(True)
        toolbar.addAction(self.step_action)

        self.back_action = QAction("Back", self) # Можна додати іконку
        self.back_action.triggered.connect(self.back) # Зв'язуємо дію із закриттям вікна
        self.back_action.setDisabled(True)
        toolbar.addAction(self.back_action)

        self.run_action = QAction("Run", self) # Можна додати іконку
        self.run_action.triggered.connect(self.run) # Зв'язуємо дію із закриттям вікна
        self.run_action.setDisabled(True)
        toolbar.addAction(self.run_action)


        #toolbar.addSeparator()

        # --- ДОДАЄМО РОЗТЯГУЮЧУ РОЗПІРКУ ---
        spacer = QWidget()
        # Встановлюємо політику розміру: Expanding по горизонталі, Expanding по вертикалі (вертикальна політика не так важлива для горизонтального тулбара)
        spacer.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Додаємо розпірку до тулбара. Все, що буде додано після неї, посунеться вправо.
        toolbar.addWidget(spacer)
        # ----------------------------------
        
        # Додавання дій (Action) до тулбара
        # Для простоти додамо дію "Вихід"
        exit_action = QAction(QIcon.fromTheme("application-exit"), "Quit", self) # Можна додати іконку
        exit_action.triggered.connect(self.quit) # Зв'язуємо дію із закриттям вікна
        toolbar.addAction(exit_action)


        # Можна також додати віджети безпосередньо до тулбара, наприклад, кнопку
        # toolbar.addWidget(QPushButton("Кнопка в тулбарі"))

        # 3. Створення та налаштування статусбара
        # QMainWindow створює статусбар автоматично при першому виклику statusBar()
        self.statusBar().setContentsMargins(10, 10, 10, 10)
        self.statusBar().showMessage("Готово") # Показуємо початкове повідомлення

        # Можна також додати тимчасові повідомлення або віджети до статусбара
        # self.statusBar().addWidget(QLabel("Додаткова інформація"))

        # === Логіка автоматичного розрахунку та фіксації розміру ===
        # 3. Розраховуємо оптимальний розмір вікна на основі вмісту
        self.adjustSize()

        # 4. Фіксуємо розмір вікна на поточному (щойно розрахованому) значенні
        self.setFixedSize(self.size())
        # =======================================================

        self.mode = lambda : {"Manual":0, "Black":1, "White":2}[self.mode_box.currentText()]
        
        self.steps: List[Step] = [Step(-1, -1, "")]*(self.n*self.n)
        self.name_c = ["", "Black", "White"]

        logger.debug("MainWindow.__init__ finshed")
        

    @Slot()
    def quit(self):
        self.close()

    @Slot()
    def new(self):
        logger.debug("MainWindow.new clicked")
        self.play()
        logger.debug("MainWindow.new finished")

    @Slot()
    def step(self):
        pass

    @Slot()
    def back(self):
        pass

    @Slot(bool)
    def run(self, r: bool):
        if self.game.is_play:
            self.statusBar().showMessage("Thinking...")
            self.game.is_busy = True
            self.game.is_run = r
            self.go(True, 0, 0)
            self.game.is_busy = False

    def play(self):

        logger.debug("MainWindow.play started")

        self.desk.init()
        #self.app.desk.draw_grid()

        self.game.is_play = True
        self.game.is_run = False
        self.game.is_busy = False

        if self.mode() == 0:
           self.step_action.setEnabled(True) #disabled = False
        else:
           self.step_action.setDisabled(True)
           self.back_action.setDisabled(True)

        self.run_action.setEnabled(True) #disabled = False
        self.mode_box.setDisabled(True) #disabled = True

        self.game.net.init()

        self.qsteps = 0
        self.add_step(7, 7, 0, "Start")

        self.mes = "Start"
        self.n_step = 1
        self.game.net.step(7, 7, 1)
        self.statusBar().showMessage("New game")

        if self.mode() == 1:
           self.run(False)

        logger.debug("MainWindow.play finished")

    # def run(self, r: bool):
    #     if self.game.is_play:
    #         self.statusBar().showMessage("Thinking...")
    #         self.game.is_busy = True
    #         self.game.is_run = r
    #         self.go(True, 0, 0)
    #         self.game.is_busy = False

    # def back(self):
    #     self.is_play = True
    #     self.is_busy = True

    #     self.replay(1)

    #     self.is_busy = False

    #     self.app.action_run.disabled = False
    #     self.app.action_step.disabled = False

    def add_step(self, x: int, y: int, c: int, mes: str):
        logger.debug(f"MainWindow.add_step({x}, {y}, {c}) started")

        self.steps[self.qsteps] = Step(x, y, mes)
        self.qsteps += 1
        self.desk.draw_step(x, y, c)

        logger.debug(f"MainWindow.add_step({x}, {y}, {c}) finished")

    def go(self, auto: bool, x: int, y: int):
        ret: int = 0
        if auto:
           ret = self.next_step()
        else:
           ret = self.manual_step(x, y)

        self.statusBar().showMessage("Finish! -> {0}".format(self.mes) if ret < 0 else "Step {0} -> {1}".format(ret, self.mes))

        if self.mode() == 0:
            self.back_action.setEnabled(True) #disabled = False

        if ret < 0 or ret > 224:
            self.run_action.setDisabled(True)
            self.step_action.setDisabled(True)
            self.mode_box.setEnabled(True) # disabled = False

            self.game.is_run = False
            self.game.is_play = False

        elif not auto and self.mode() > 0:
            self.go(True, 7, 7)
        elif self.game.is_run:
            self.go(True, 7, 7)

    def next_step(self):
        self.n_step += 1

        if self.game.check_win(3 - (2 - self.n_step % 2)) or self.game.check_draw():
            return -1
        else:
            p = self.game.calc_point(2 - self.n_step % 2)
            self.game.net.step(p.x, p.y, 2 - self.n_step % 2)
            self.add_step(p.x, p.y, 1 - self.n_step % 2, self.mes)
            return self.n_step

    def manual_step(self, x: int, y: int):
        self.n_step += 1
        if self.game.check_win(3 - (2 - self.n_step % 2)) or self.game.check_draw():
            return -1
        else:
            self.game.net.step(x, y, 2 - self.n_step % 2)
            self.mes = "{0}  :: manual ({1},{2})".format(self.name_c[2 - self.n_step % 2], x, y )
            self.add_step(x, y, 1 - self.n_step % 2, self.mes)
            return self.n_step

    
def main():
    logger.info("Старт програми.")

    app = QApplication(sys.argv) # Передаємо аргументи командного рядка
    
    win = MainWindow() # Створюємо екземпляр головного вікна
    win.show() # Показуємо вікно
    ret = app.exec() # Запускаємо цикл подій

    logger.info("Програма завершена.")

    sys.exit(ret) 