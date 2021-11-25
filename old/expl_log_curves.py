# %%
import numpy as np
import math, copy
from matplotlib import pyplot as plt
from shapely.geometry import LineString

from local_utils import euclidian_dst, rl_inverse, draw, intersect


# %%
class ShiftedLogCurve(): 

    def __init__(self, a=1, b=1, root=(0,0), leaf=(0,20), vbs = False, run=False):
        '''
        КОНСТРУКТОР
        Инициализирует параметры кривой. Переводит координаты корня и листа в полярные координаты
        a: радиус кривизны
        b: производная
        root: координаты корня
        leaf: координаты листа
        vbs: verbose output? True/False
        run: Если True, запускаются функции eval и кривая строится после инициализации (определяются координаты точек)
        
        self.th: область определения функции (диапазон параметра t)
        '''
        self.a = a # Радиус кривизны
        self.b = b # Производная
        self.th = np.linspace(0, np.pi, 100) # Область определения в полярных координатах (угол в радианах)
        self.root = root # Координаты корня
        self.leaf = leaf # Координаты листа
        self.vbs = vbs # verbose?
        self.run = run # run?
        self.ang = None # Дирекционный угол в радианах (против часовой стрелки от оси x)
        self.dst = None # Расстояние между корнем и листом

        self._pts_to_polar()
        
        self.crds = None # Прямоугольные координаты
        self.r = None # Массив r(th) радиусов в полярных координатах
        if run:
            self.eval_a()
            self._eval_r(self.th)
            self.proj_rect()
        
    
    def _pts_to_polar(self):
        '''
        ПЕРЕВОД В ПОЛЯРНЫЕ КООРДИНАТЫ (0° вправо, отсчёт против часовой стрелки)
        Для построения кривой между корнем и листом необходимо подобрать параметр a при фиксированном b.
        Для этого в данной реализации необходимо знать расстояние от корня до листа.
        Азимут нужен для обратного перевода кривой в прямоугольные координаты
        
        формат координат: (ось абсцисс, ось ординат)
        
        return не предусмотрен.
        Модифицируются:
        self.ang: азимут
        self.dst: расстояние
        '''
        dx = self.leaf[0] - self.root[0]
        dy = self.leaf[1] - self.root[1]
        if self.vbs: print("dx: ", dx, "dy: ", dy)
        try:
            self.ang = np.arctan2(dy, dx)
        except ZeroDivisionError:
            self.ang = -np.pi/2 # Ловим деление на 0 при dx = 0
        if self.vbs: print("angle: ", np.degrees(self.ang))
        self.dst = np.sqrt(dx**2 + dy**2)
        if self.vbs: print("distance: ", self.dst)
    
    def _eval_r(self, th):
        '''
        ОПРЕДЕЛЕНИЕ ЗНАЧЕНИЙ РАДИУСА ДЛЯ ОБЛАСТИ ОПРЕДЕЛЕНИЙ (углов)
        Экспонента сдвинута на -1.
        Таким образом область значений сдвигается на -self.a относительно лог. спирали по определению
        Это необходио, чтобы область значений начиналась от 0
        th: np.array область определения (массив углов для котрых требуется рассчитать радиус)
        
        return: np.array значения функции в полярных координатах
        '''
        self.r = self.a*(np.exp(self.b*th)-1)
        return self.a*(np.exp(self.b*th)-1)
    
    def proj_rect(self, r=None):
        '''
        ПЕРЕВОД В ПРЯМОУГОЛЬНЫЕ КООРДИНАТЫ
        Функция переводит кривую в полярных координатах (массив R(th) для массива th) в прямоугольные (массив x и массив y)
        Результат: редактирование атрибута self.crds

        input: обязательных аргументов нет
        R: массив R(th). Если None, то используется self.R

        return: self.crds (на всякий случай)
        '''
        if r is None:
            r = self.r
        thr = self.th + self.ang + np.pi
        thl = -self.th + self.ang + np.pi
        xr = r*np.cos(thr)
        yr = r*np.sin(thr)
        xl = r*np.cos(thl)
        yl = r*np.sin(thl)
        self.crds = {"right_xy": [xr, yr], "left_xy": [xl, yl]}
        return self.crds
    
    def eval_r(self, th=None, run=False):
        '''
        ОПРЕДЕЛЕНИЕ ЗНАЧЕНИЙ РАДИУСА ДЛЯ ОБЛАСТИ ОПРЕДЕЛЕНИЙ (углов)
        Функция вызова
        Вызывает _eval_r с заданной областью определения (th).
        Если область не задана, используется инициализированная ([0, np.pi])
        
        th: np.array
        run: Если True, то объект подлежит изменению. Если False, то объект не будет изменён

        return: np.array значения функции в полярных координатах
        
        '''
        if (th is None) and run:
            return self._eval_r(self.th)
        elif not(th is None) and run:
            return self._eval_r(th)
        elif th is None:
            return self.a*(np.exp(self.b*self.th)-1)
        else:
            return self.a*(np.exp(self.b*th)-1)

    def eval_a(self):
        '''
        РАСЧЁТ self.a
        Рассчитывает параметр a, который нужно использовать, чтобы "вписать" кривую с заданным b
        между корнем и листом
        Экспонента сдвинута на -1
        
        Входных параметров и return не предусмотрено
        '''
        self.a = self.dst/(np.exp(self.b*np.pi)-1)
    
    def draw(self):
        # Отрисовка кривой внутри области определения
        fig = plt.figure(1,(15,15))
        ax1 = fig.add_subplot(221,polar=True) # раскомментировать эту строку и "222" для отображения в полярных координатах
        ax2 = fig.add_subplot(222,polar=False)
        
        xr,yr = self.proj_rect()["right_xy"]
        xl,yl = self.proj_rect()["left_xy"]
        ax1.plot(self.th, self.r, "-c")
        ax1.plot(-self.th, self.r, "-m")
        ax2.plot(xr,yr, "-c")
        ax2.plot(xl,yl, "-m")
        ax2.plot(self.leaf[0], self.leaf[1], "og")
        ax2.plot(self.root[0], self.root[1], "sg")
        ax2.set_aspect(1)
    
    # Геттеры

    def get_polar(self, tp="right"):
        """
        tp = "right"/"left" (тип спирали: правая или левая)
        """
        if tp == "right":
            return (self.th, self.r)
        elif tp == "left":
            return (-self.th, self.r)
        else:
            raise ValueError('tp has to be "right" or "left"')
    
    def get_rect(self, tp="right"):
        """
        tp = "right"/"left" (тип спирали: правая или левая)
        """
        if tp in ("right", "left"):
            return (self.crds[f"{tp}_xy"][0], self.crds[f"{tp}_xy"][1])
        else:
            raise ValueError('tp has to be "right" or "left"')

            


# %%
class LimitedSLC(ShiftedLogCurve):
    '''
    Дополнительные атрибуты:
    tp - тип. Принимает значения 'right' и 'left'
    upperlimit_xy - координаты верхней границы
    lowerlimit_xy - координаты нижней границы

    
    '''
    def draw(self):
        # Отрисовка кривой внутри области определения
        fig = plt.figure(1,(15,15))
        ax1 = fig.add_subplot(221,polar=True) # раскомментировать эту строку и "222" для отображения в полярных координатах
        ax2 = fig.add_subplot(222,polar=False)
        
        x,y = self.proj_rect()[f"{self.tp}_xy"]
        
        if self.tp == 'right':
            sign = -1
            color = 'c'
        else:
            sign =1
            color = 'm'

        ax1.plot(self.th*sign, self.r, f"-{color}")
        
        ax2.plot(x,y, f"-{color}")


        ax2.plot(self.lowerlimit_xy[0], self.lowerlimit_xy[1], "^k")
        ax2.plot(self.upperlimit_xy[0], self.upperlimit_xy[1], "vk")

        ax2.plot(self.leaf[0], self.leaf[1], "og")
        ax2.plot(self.root[0], self.root[1], "sg")

        ax2.set_aspect(1)
    
    def batch_draw(self, ax1, ax2):
        # Добавление кривой на передаваемый график
        
        x,y = self.proj_rect()[f"{self.tp}_xy"]
        
        if self.tp == 'right':
            sign = -1
            color = 'c'
        else:
            sign =1
            color = 'm'

        ax1.plot(self.th*sign, self.r, f"-{color}")
        
        ax2.plot(x,y, f"-{color}")
        ax2.plot(self.lowerlimit_xy[0], self.lowerlimit_xy[1], "^k")
        ax2.plot(self.upperlimit_xy[0], self.upperlimit_xy[1], "vk")
        ax2.plot(self.leaf[0], self.leaf[1], "og")
        ax2.plot(self.root[0], self.root[1], "sg")
        ax2.set_aspect(1)
    

    def crop(self, tp, upperlimit_xy=None, lowerlimit_xy=None):
        '''
        Вырезание кривой между точками
        '''
        # Проверки и определения
        assert tp in ('right', 'left'), "tp must be assigned"

        self.tp = tp
        self.upperlimit_xy = upperlimit_xy
        self.lowerlimit_xy = lowerlimit_xy

        upperlimit_th = lowerlimit_th = None

        if upperlimit_xy is None:
            self.upperlimit_xy = self.leaf
            upperlimit_th = np.pi
        if lowerlimit_xy is None:
            self.lowerlimit_xy = self.root
            lowerlimit_th = 0
        
        # Расчет
        if tp == 'right': sign = -1
        else: sign =1

        if upperlimit_th is None:
            upperlimit_th = np.pi + self.ang*sign - np.arctan2(upperlimit_xy[1]-self.root[1], upperlimit_xy[0]-self.root[0])
        if lowerlimit_th is None:
            lowerlimit_th = np.pi + self.ang*sign - np.arctan2(lowerlimit_xy[1]-self.root[1], lowerlimit_xy[0]-self.root[0])

        # Запись результата
        self.th = np.linspace(lowerlimit_th, upperlimit_th, 100)
        # Перевычисление радиусов для новых th
        self.eval_r(run=True)
        
    def get_dst2(self):
        try:
            return np.sqrt((self.upperlimit_xy[0]-self.lowerlimit_xy[0])**2 + (self.upperlimit_xy[1]-self.lowerlimit_xy[1])**2)
        except AttributeError:
            return self.dst



# %%
class FlowTreeBuilder():

    def __init__(self, root=(0,0), leaves=[ (17, -4), (20, 7), (-10, 15), (-5, 20), (-8, -20)], b=1.9):
        self.root = root
        self.leaves = leaves
        self.b = b
        self.data = []
        self.main_exec()
    
    def main_exec(self):

        for leaf in self.leaves:
            pass
            #найти все пересечения
            #добавить пересечения в список активных точек
            #в списке активных точек хранится некий метод вместе ссылкой на точку

        return


expl = FlowTreeBuilder()


# %%
# expl = FlowTreeBuilder()
