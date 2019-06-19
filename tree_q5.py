from model_builder import TreeBuilder
from design import Ui_Dialog

from PyQt5 import QtWidgets, QtCore
import sys


class Window(QtWidgets.QMainWindow):
    def __init__(self):
        super(Window, self).__init__()
        self.ui = Ui_Dialog()
        self.ui.setupUi(self)

        # дерево с барьером
        tree = TreeBuilder(s="6", b="0.2", c="0.1", a="-0.1", r="0.15",
                           m="7", b2="0.15", c2="0.05", a2="-0.05", r2="0.05")

        # дерево без барьера
        #tree = TreeBuilder(s="6", b="0.2", c="0.1", a="-0.1", r="0.15")

        # строим дерево и выбираем количество слоёв от корня
        #n = self.ui.n.setReadOnly(True)
        tree.build_tree(2)

        # рисуем дерево
        #tree.draw_tree()

        # считаем капитал
        x = tree.calc_capital()


        # Меняем текст
        self.ui.print.setText(f"Верхняя цена: {x['x_down']}\n\nНижняя цена: {x['x_up']}")


app = QtWidgets.QApplication([])
application = Window()
application.show()

sys.exit(app.exec())