from copy import deepcopy
from decimal import Decimal

import matplotlib.pyplot as plt
import networkx as nx


class TreeBuilder:

    def __init__(self, s, b, c, a, r,
                 m="0.0", b2="0.0", c2="0.0", a2="0.0", r2="0.0"):
        """
        :param s: стоимость акции на нулевом уровне type: string
        :param b: дельта =  1  type: string
        :param c: дельта =  0  type: string
        :param a: дельта = -1  type: string
        """
        self.s = Decimal(s)
        self.b = Decimal(b)
        self.c = Decimal(c)
        self.a = Decimal(a)
        self.r = Decimal(r)

        self.m = Decimal(m)
        self.b2 = Decimal(b2)
        self.c2 = Decimal(c2)
        self.a2 = Decimal(a2)
        self.r2 = Decimal(r2)

        # создаём корень дерева (нулевой уровень)
        root = nx.DiGraph()
        root.add_node(('0.0', s))

        # дерево и первый лист
        self.tree = root
        self.leaves = [('0.0', s)]

    def build_tree(self, number_of_levels):
        """
        построить дерево, расчитыая стоимость акций
        в кадом листе
        :param number_of_levels: количество уровней в дереве
        """
        for level in range(number_of_levels):
            self.__add_level(level+1)

    def draw_tree(self):
        """
        нарисовать дерево
        """
        options = {
            'with_labels': True,
            'node_color': 'PowderBlue',
            'node_size': 1000,
            'width': 1
        }

        nx.draw_planar(self.tree, **options)
        plt.show()

    def calc_capital(self):
        """

        :return:
        """
        self.__calc_x_for_leaves()
        self.__get_full_leaves()

        node_with_x_up = self.leaves
        node_with_x_down = self.leaves

        while len(node_with_x_up) != 1:
            node_with_x_up = self.__get_parents_x(node_with_x_up, "up")
            node_with_x_down = self.__get_parents_x(node_with_x_down, "down")

        return {"x_up": str(node_with_x_up[0][1]['x']),
                "x_down": str(node_with_x_down[0][1]['x'])}

    ############## Private methods calc_capital ##############

    def __calc_x_for_leaves(self):
        """
        расчитать капитал x на листьях
        """
        for leaf in self.leaves:
            x = Decimal(leaf[1]) - self.s
            if x < 0:
                x = Decimal('0')
            self.tree.add_node(leaf, x=x)

    def __get_full_leaves(self):
        """
        для каждого листа сохранить его капитал x
        """
        all_nodes = self.tree.nodes.data()
        data_leaves = []

        for leaf in self.leaves:
            for node in all_nodes:
                if leaf == node[0]:
                    data_leaves.append(node)

        self.leaves = data_leaves

    def __get_parents_x(self, nodes_with_x, border):
        """

        :param nodes_with_x:
        :return:
        """
        # находим предков данных узлов
        set_parents = set()

        for node in nodes_with_x:
            parent = list(self.tree.predecessors(node[0]))
            set_parents.add(parent[0])

        # создадим список словарей с предками
        list_parent_and_sons = []

        for parent in set_parents:
            list_parent_and_sons.append({'parent': parent})

        # сопоставим предков с потомками [{предок, потомок_1, 2, 3}..{..}]
        for node in nodes_with_x:
            for i in range(len(list_parent_and_sons)):
                if list_parent_and_sons[i]['parent'] == (list(self.tree.predecessors(node[0])))[0]:
                    x = self.__up_or_mid_or_down(node)
                    list_parent_and_sons[i].update(x)

        # посчитать значения родителей и составить с ними новый список листьев
        result = []

        for record in list_parent_and_sons:
            if self.m == Decimal("0.0"):
                parent_x = self.calc_price(record['x_1'], record['x_2'], record['x_3'], border, m=False)
            else:
                if Decimal(record['parent'][1]) > self.m:
                    parent_x = self.calc_price(record['x_1'], record['x_2'], record['x_3'], border, m=True)
                else:
                    parent_x = self.calc_price(record['x_1'], record['x_2'], record['x_3'], border, m=False)
            result.append((record['parent'], {'x': parent_x}))
            print((record['parent'], {'x': parent_x}))

        return result

    @staticmethod
    def __up_or_mid_or_down(node):
        """

        :param node:
        :return:
        """
        number = int(((node[0][0]).split('.'))[1])
        if number % 3 == 0:
            return {'x_1': node[1]['x']}
        if number % 3 == 1:
            return {'x_2': node[1]['x']}
        if number % 3 == 2:
            return {'x_3': node[1]['x']}

    def calc_price(self, x1, x2, x3, border, m):

        if m is True:
            r = self.r2
            a = self.a2
            b = self.b2
            c = self.c2
        elif m is False:
            r = self.r
            a = self.a
            b = self.b
            c = self.c

        p = None

        if border == "up":
            p = (r - a) / (b - a)
        elif border == "down":
            p = (r - c) / (b - a)

        q = (r - a - (b - a) * p) / (c - a)
        price = x1 * p + x2 * q + x3 * (Decimal("1") - p - q)

        return price

    ############### Private methods build_tree ###############

    def __add_level(self, level):
        """
        добавить в дерево один уровень
        :param level: номер уровня, который добавляем
        """
        old_leaves = deepcopy(self.leaves)
        self.leaves = []

        # считаем номер листа на уровне
        leaves_counter = 0

        for leaf in old_leaves:
            leaves_counter = self.__add_three_leaves(leaf, level, leaves_counter)

    def __add_three_leaves(self, leaf, level, leaves_counter):
        """
        расчитать три потомка от родителя
        :param leaf: предок
        :param level: уровень потомка
        :param leaves_counter: номер потомка на данном уровне
        :return номер последнего листа на данном уровне
        """
        # расчитываем значения для трёх потомков
        s = Decimal(leaf[1])
        shares_values = self.__calc_shares_values(s)

        for position in ['1', '0', '-1']:
            number = f"{level}.{leaves_counter}"
            new_leaf = (number, shares_values[position])
            leaves_counter += 1

            self.tree.add_edge(leaf, new_leaf)
            self.leaves.append(new_leaf)

        return leaves_counter

    def __calc_shares_values(self, s):
        """
        расчитать стоимости акций
        для следующего уровя дерева
        :param s: стоимость акции на предыдущем уровне type: string
        :return: значения стоимости акций для трёх потомков
        """
        if self.m != Decimal("0.0"):
            if s < self.m:
                up_share_s = s * (1 + self.b)
                mid_share_s = s * (1 + self.c)
                down_share_s = s * (1 + self.a)
            else:
                up_share_s = s * (1 + self.b2)
                mid_share_s = s * (1 + self.c2)
                down_share_s = s * (1 + self.a2)
        else:
            up_share_s = s * (1 + self.b)
            mid_share_s = s * (1 + self.c)
            down_share_s = s * (1 + self.a)

        return {
                   "1": str(up_share_s),
                   "0": str(mid_share_s),
                   "-1": str(down_share_s)
               }

    ##########################################################


if __name__ == '__main__':

    # дерево с барьером
    tree = TreeBuilder(s="6", b="0.2", c="0.1", a="-0.1", r="0.15",
                       m="7", b2="0.15", c2="0.05", a2="-0.05", r2="0.05")

    # дерево без барьера
    # tree = TreeBuilder(s="6", b="0.2", c="0.1", a="-0.1", r="0.15")

    # строим дерево и выбираем количество слоёв от корня
    tree.build_tree(2)

    # рисуем дерево
    tree.draw_tree()

    # считаем капитал
    x = tree.calc_capital()
    print(x)
