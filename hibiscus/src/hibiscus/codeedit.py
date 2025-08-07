from pyqode.python import widgets
from pyqode.python.backend import server


class WorkCodeEdit(widgets.PyCodeEdit):
    def __init__(self, text: str):
        super().__init__(server_script=server.__file__)
        self.setPlainText(text)
        

        
