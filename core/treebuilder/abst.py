class AbstractBSTData():
    def set_node(self, node):
        self.node = node
    
    def unpack(self):
        return None
    
    def __gt__(self, other):
        return self.unpack() > other.unpack()
        
    def __lt__(self, other):
        return self.unpack() < other.unpack()
    
    def __ge__(self, other):
        return self.unpack() >= other.unpack()
    
    def __le__(self, other):
        return self.unpack() <= other.unpack()
    
    def __repr__(self):
        return f"{self.unpack()}"


class SearchTreeNode:
    
    def __init__(self, val):
        self.red = False
        self.parent = None
        if isinstance(val, AbstractBSTData):
            self.val = val
            # val.set_node(self) !!! Do we need this line?
        else:
            raise ValueError("data must be enharited from AbstractBSTData")
        self.left = None
        self.right = None
    
    def __repr__(self):
        return f"{self.val}"
    
    def __call__(self, *args, **kwargs):
        return self.val(*args, **kwargs, abstnd=self)


class AbstractSearchTree:
    
    def __init__(self):
        """Red-Black binary search tree"""
        self.nil = SearchTreeNode(AbstractBSTData())
        self.nil.red = False
        self.nil.left = self.nil
        self.nil.right = self.nil
        self.nil.parent = self.nil
        self.root = self.nil
        self.__counter = 0
    
    
    def insert(self, val):
        print(f"Inserting to {type(self)}: ", val)
        self._count()
        z = SearchTreeNode(val)

        y = self.nil
        x = self.root
        while x != self.nil:
            y = x
            if z.val < x.val:
                x = x.left
            elif z.val > x.val:
                x = x.right
            else:
                raise Warning("equal data in nodes")
        z.parent = y
        if y == self.nil:
            self.root = z
        elif z.val < y.val:
            y.left = z
        else:
            y.right = z
        z.left = self.nil
        z.right = self.nil
        z.red = True
        self._fix_insert(z)
        return z
    
    def _fix_insert(self, z):
        while z.parent.red == True:
            if z.parent == z.parent.parent.left:
                y = z.parent.parent.right
                # CASE 1
                if y.red == True:
                    z.parent.red = False
                    y.red = False
                    z.parent.parent.red = True
                # CASE 2
                elif z == z.parent.right:
                    z = z.parent
                    self.rotate_left(z)
                # CASE 3
                else:
                    z.parent.red = False
                    z.parent.parent.red = True
                    self.rotate_right(z.parent.parent)
            else:
                y = z.parent.parent.left
                # CASE 1
                if y.red == True:
                    z.parent.red = False
                    y.red = False
                    z.parent.parent.red = True
                # CASE 2
                elif z == z.parent.left:
                    z = z.parent
                    self.rotate_right(z)
                # CASE 3
                else:
                    z.parent.red = False
                    z.parent.parent.red = True
                    self.rotate_left(z.parent.parent)

        self.root.red = False
        # self.root.parent = self.nil # !!! Do we need this???

    def _delete(self, z): # variables names from T.H.Cormen Introduction to algorithms
        print(f"Deleting from {type(self)}: ", z.val)
        self._uncount()
        if self.__counter == 0:
            print(f"COUNTER = ZERO at {type(self)}")
            self.root = self.nil
            return self.root
        if z.left == self.nil or z.right == self.nil:
            y = z
        else:
            y = self.succ(z)
        
        if y.left != self.nil:
            x = y.left
        else:
            x = y.right
        
        x.parent = y.parent

        if y.parent == self.nil:
            self.root = x
        elif y == y.parent.left:
            y.parent.left = x
        else:
            y.parent.right = x
        
        if y != z:
            z.val = y.val
        if y.red == False:
            self._fix_delete(x)
        return y
    
    def _fix_delete(self, x):
        while x != self.root and x.red == False:
            if x == x.parent.left:
                w = x.parent.right
                # CASE 1
                if w.red == True:
                    w.red = False
                    x.parent.red = True
                    self.rotate_left(x.parent)
                    w = x.parent.right
                # CASE 2
                if w.left.red == False and w.right.red == False:
                    w.red = True
                    x = x.parent
                # CASE 3
                else:
                    if w.right.red == False:
                        w.left.red = False
                        w.red = True
                        self.rotate_right(w)
                        w = x.parent.right
                # CASE 4
                    w.red = x.parent.red
                    x.parent.red = False
                    w.right.red = False
                    self.rotate_left(x.parent)
                    x = self.root
            else:
                w = x.parent.left
                # CASE 1
                if w.red == True:
                    w.red = False
                    x.parent.red = True
                    self.rotate_right(x.parent)
                    w = x.parent.left
                # CASE 2
                if w.right.red == False and w.left.red == False:
                    w.red = True
                    x = x.parent
                # CASE 3
                else:
                    if w.left.red == False:
                        w.right.red = False
                        w.red = True
                        self.rotate_left(w)
                        w = x.parent.left
                # CASE 4
                    w.red = x.parent.red
                    x.parent.red = False
                    w.left.red = False
                    self.rotate_right(x.parent)
                    x = self.root
        x.red = False

    def delete_by_val(self, val):
        z = self.get_nd_by_val(val)
        if z is not None: self._delete(z)

    def __pred(self, node):
        if node == self.root:
            return None
        elif node.parent.right == node:
            return node.parent
        else:
            return self.__pred(node.parent)

    def pred(self, node):
        if node.left != self.nil:
            return self.__max(node.left)
        else:
            return self.__pred(node)

    def __succ(self, node):
        if node == self.root:
            return None
        elif node.parent.left == node:
            return node.parent
        else:
            return self.__succ(node.parent)

    def succ(self, node):
        if node.right != self.nil:
            return self.__min(node.right)
        else:
            return self.__succ(node)

    def rotate_left(self, x):
        y = x.right
        x.right = y.left
        if y.left != self.nil:
            y.left.parent = x
        y.parent = x.parent
        if x.parent == self.nil:
            self.root = y
        elif x == x.parent.left:
            x.parent.left = y
        else:
            x.parent.right = y
        y.left = x
        x.parent = y


    def rotate_right(self, x):
        y = x.left
        x.left = y.right
        if y.right != self.nil:
            y.right.parent = x
        y.parent = x.parent
        if x.parent == self.nil:
            self.root = y
        elif x == x.parent.right:
            x.parent.right = y
        else:
            x.parent.left = y
        y.right = x
        x.parent = y
    
    def __max(self, node):
        '''max element in subtree with node as root'''
        if node.right == self.nil:
            return node
        else:
            return self.__max(node.right)

    def get_max(self):
        return self.__max(self.root)

    def __min(self, node):
        '''min element in subtree with node as root'''
        if node.left == self.nil:
            return node
        else:
            return self.__min(node.left)

    def get_min(self):
        return self.__min(self.root)
    
    def _get_nd_by_val(self, searchRoot, val):
        if searchRoot == self.nil:
            return None
        elif val == searchRoot.val:
            return searchRoot
        elif val > searchRoot.val:
            return self._get_nd_by_val(searchRoot.right, val)
        elif val < searchRoot.val:
            return self._get_nd_by_val(searchRoot.left, val)
    
    def get_nd_by_val(self, val: SearchTreeNode):
        return self._get_nd_by_val(self.root, val)

    def get_nbhood(self, node):
        '''
        return: (predecessor, succwer)
        '''
        return (self.pred(node), self.succ(node))

    def _count(self):
        self.__counter += 1

    def _uncount(self):
        self.__counter -= 1

    def __len__(self):
        return self.__counter



if __name__ == "__main__":
    import random
    import numpy as np

    def print_tree(node, lines, level=0):
        if node.val.unpack() is not None:
            print_tree(node.left, lines, level + 1)
            lines.append('-' * 4 * level + '> ' +
                         str(node.val.unpack()) + ' ' + ('r' if node.red else 'b'))
            print_tree(node.right, lines, level + 1)

    class Point(AbstractBSTData):

        def __init__(self, data):
            self.data = data
        
        def unpack(self):
            return self.data
        
        def __repr__(self):
            return f"{self.data}"

    tree = AbstractSearchTree()
    numbers = random.sample(range(360), 100)
    numbers = np.random.randint(14, size=(15))
    points = []
    for n in numbers:
        point = Point(n)
        tree.insert(point)
        points.append(point)
    
    lines = []
    print_tree(tree.root, lines)
    print('\n'.join(lines))
    print (points)
