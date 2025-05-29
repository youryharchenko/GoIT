from __future__ import annotations
import logging
import sys
import random
from typing import List, Tuple

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

class Point:
    def __init__(self, net: Net, x: int, y: int):
        self.net = net
        self.x = x
        self.y = y
        self.slots: List[Slot] = []
        self.r = [0, 0, 0]
        self.s = 0

    def is_valid_scp(self, d: int):
        x = self.x - 7
        y = self.y - 7
    # 0 - vert, 1 - horiz, 2 - up, 3 - down
        if d == 0 and y > -6 and y < 6:
            return True
        if d == 1 and x > -6 and x < 6:
            return True
        if d == 2 and (x > -6 and y < 6) and (x < 6 and y > -6):
            return True
        if d == 3 and (x > -6 and y > -6) and (x < 6 and y < 6):
            return True
        return False

    def add_slot(self, s: Slot):
        self.slots.append(s)
        self.r[s.s] += 1

    def __repr__(self):
        return f"Point({self.x},{self.y})"

class Slot:
    def __init__(self, net: Net, scp: Point, d: int):
        self.net = net
        self.scp = scp
        self.d = d
        self.points: List[Point] = [Point(net, -1, -1)] * 5
        self.r = 0
        self.s = 0

    def init(self):
        #print "Init Slot: d: {0}, scp: {1}".format(self.d, self.scp.to_string())
        self.points[2] = self.net.get_point(self.scp.x, self.scp.y)

        if self.d == 0:
            self.points[0] = self.net.get_point(self.scp.x, self.scp.y - 2)
            self.points[1] = self.net.get_point(self.scp.x, self.scp.y - 1)
            self.points[3] = self.net.get_point(self.scp.x, self.scp.y + 1)
            self.points[4] = self.net.get_point(self.scp.x, self.scp.y + 2)
        elif self.d == 1:
            self.points[0] = self.net.get_point(self.scp.x - 2, self.scp.y)
            self.points[1] = self.net.get_point(self.scp.x - 1, self.scp.y)
            self.points[3] = self.net.get_point(self.scp.x + 1, self.scp.y)
            self.points[4] = self.net.get_point(self.scp.x + 2, self.scp.y)
        elif self.d == 2:
            self.points[0] = self.net.get_point(self.scp.x - 2, self.scp.y - 2)
            self.points[1] = self.net.get_point(self.scp.x - 1, self.scp.y - 1)
            self.points[3] = self.net.get_point(self.scp.x + 1, self.scp.y + 1)
            self.points[4] = self.net.get_point(self.scp.x + 2, self.scp.y + 2)
        elif self.d == 3:
            self.points[0] = self.net.get_point(self.scp.x - 2, self.scp.y + 2)
            self.points[1] = self.net.get_point(self.scp.x - 1, self.scp.y + 1)
            self.points[3] = self.net.get_point(self.scp.x + 1, self.scp.y - 1)
            self.points[4] = self.net.get_point(self.scp.x + 2, self.scp.y - 2)

        for i in range(0, 5):
            self.points[i].add_slot(self)

class Net:
    def __init__(self, n: int):
        logger.debug("Net.__init__ started")
        self.n = n
        logger.debug("Net.__init__ finished")

    def init(self):

        logger.debug("Net.init started")

        self.all_slots: List[Slot] = []
        self.active_slots: List[List[Slot]] = [[], [], []]  # free, black, white

        self.all_points = [Point(self, int(i / self.n), i % self.n) for i in range(0, self.n*self.n)]

        #logger.debug(f"Net.init all_points: {self.all_points}")
        
        self.empty_points = self.all_points[:]

        for p in self.all_points:
            for d in range(0, 4):
                if p.is_valid_scp(d):
                    s = Slot(self, p, d)
                    self.all_slots.append(s)

        self.active_slots[0] = self.all_slots[:]
        for s in self.all_slots:
            s.init()

        logger.debug("Net.init finished")

    def step(self, x: int, y: int, c: int):

        logger.debug(f"Net.step({x}, {y}, {c}) started")

        p = self.get_point(x, y)
        p.s = c
        self.empty_points.remove(p)

        for s in p.slots:
            if s.s == 0:
                p.r[0] -= 1
                p.r[c] += 1
                s.s = c
                s.r = 1
                self.active_slots[0].remove(s)
                self.active_slots[c].append(s)
            elif s.s == c:
                p.r[c] += 1
                s.r += 1
            elif s.s != 3:
                p.r[c] -= 1
                self.active_slots[s.s].remove(s)
                s.s = 3

        logger.debug(f"Net.step({x}, {y}, {c}) finished")

    def get_point(self, x: int, y: int):
        #print (x, y)
        p = self.all_points[x * self.n + y]
        #logger.debug(f"Net.get_point({x}, {y}) -> {p}")
        return p

class Game:
    def __init__(self, n: int):

        logger.debug("Game.__init__ started")

        self.net = Net(n)

        self.is_play = False
        self.is_run = False
        self.is_busy = False

        self.n_step = 0
        self.mes = ""

        #self.main = main
        self.name_c = ["", "Black", "White"]

        logger.debug("Game.__init__ finished")

    def check_win(self, c: int):
        for s in self.net.active_slots[c]:
            if s.r == 5:
                self.mes = self.name_c[c] + " :: win!!!"
                return True
        return False

    def check_draw(self):
        if len(self.net.active_slots[0]) == 0 and \
                len(self.net.active_slots[1]) == 0 and \
                len(self.net.active_slots[2]) == 0:
            self.mes = " draw :("
            return True
        else:
            return False

    def calc_point(self, c: int) -> Point:
        logger.debug(f"Game.calc_point({c}) started")

        self.mes = self.name_c[c] + " :: auto :: "

        ret = self.find_slot_4(c)
        if len(ret) == 0:
            ret = self.find_slot_4(3 - c)
        if len(ret) == 0:
            ret = self.find_point_x(c, 2, 1)

        if len(ret) == 0:
            ret = self.find_point_x(3 - c, 2, 1)
        if len(ret) == 0:

            ret = self.find_point_x(c, 1, 5)
        if len(ret) == 0:
            ret = self.find_point_x(3 - c, 1, 5)
        if len(ret) == 0:

            ret = self.find_point_x(c, 1, 4)
        if len(ret) == 0:
            ret = self.find_point_x(3 - c, 1, 4)

        if len(ret) == 0:
            ret = self.find_point_x(c, 1, 3)
        if len(ret) == 0:
            ret = self.find_point_x(3 - c, 1, 3)

        if len(ret) == 0:
            ret = self.find_point_x(c, 1, 2)
        if len(ret) == 0:
            ret = self.find_point_x(3 - c, 1, 2)

        if len(ret) == 0:
            ret = self.find_point_x(c, 1, 1)
        if len(ret) == 0:
            ret = self.find_point_x(3 - c, 1, 1)

        if len(ret) == 0:
            ret = self.find_point_x(c, 0, 10)
        if len(ret) == 0:
            ret = self.find_point_x(3 - c, 0, 10)

        if len(ret) == 0:
            ret = self.find_point_x(c, 0, 9)
        if len(ret) == 0:
            ret = self.find_point_x(3 - c, 0, 9)

        if len(ret) == 0:
            ret = self.find_point_x(c, 0, 8)
        if len(ret) == 0:
            ret = self.find_point_x(3 - c, 0, 8)

        if len(ret) == 0:
            ret = self.find_point_x(c, 0, 7)
        if len(ret) == 0:
            ret = self.find_point_x(3 - c, 0, 7)

        if len(ret) == 0:
            ret = self.calc_point_max_rate(c)
    
        o = random.choice(ret)
        self.mes = o[1]
        return o[0]

    def find_slot_4(self, c: int):
        ret: List[Tuple[Point, str]] = []
        m = 0
        for s in self.net.active_slots[c]:
            if s.r == 4:
                for p in s.points:
                    if p.s == 0:
                        m = "{0} {1} :: find_slot_4 -> -> ({2},{3})".format(self.mes, self.name_c[c], p.x, p.y)
                        ret.append((p, m))
        return ret

    def find_point_x(self, c: int, r: int, b: int):
        ret: List[Tuple[Point, str]] = []
        m = ""
        for p in self.net.empty_points:
            i = 0
            for s in p.slots:
                if s.s == c and s.r > r:
                    i += 1
            if i > b:
                m = "{0} {1} :: find_point_x({2},{3}) -> ({4},{5})".format(self.mes, self.name_c[c], r, b, p.x, p.y)
                ret.append((p, m))

        return ret

    def calc_point_max_rate(self, c: int):
        ret: List[Tuple[Point, str]] = []
        m = ""
        r = -1
        d = 0
        i = 0

        for p in self.net.empty_points:
            d = 0
            for s in p.slots:
                if s.s == 0:
                    d += 1
                elif s.s == c:
                    d += (1 + s.r) * (1 + s.r)
                elif s.s != 3:
                    d += (1 + s.r) * (1 + s.r)

            if d > r:
                i = 1
                r = d
                ret = []
                m = "{0} {1} :: point_max_rate({2},{3}) -> ({4},{5})".format(self.mes, self.name_c[c], i, r, p.x, p.y)
                ret.append((p, m))
            elif d == r:
                i += 1
                m = "{0} {1} :: point_max_rate({2},{3}) -> ({4},{5})".format(self.mes, self.name_c[c], i, r, p.x, p.y)
                ret.append((p, m))

        return ret

   