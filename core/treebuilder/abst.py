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


class AbstractSearchTree:
    
    def __init__(self):
        """Red-Black binary search tree"""
        self.nil = SearchTreeNode(AbstractBSTData())
        self.nil.red = False
        self.nil.left = None
        self.nil.right = None
        self.root = self.nil
        self.__counter = 0
    
    
    def insert(self, val):
        self._count()
        new_node = SearchTreeNode(val)
        new_node.parent = None
        new_node.left = self.nil
        new_node.right = self.nil
        new_node.red = True
        
        parent = None
        current = self.root
        while current != self.nil:
            parent = current
            if new_node.val < current.val:
                current = current.left
            elif new_node.val > current.val:
                current = current.right
            else:
                raise Warning("equal data in nodes")
        
        new_node.parent = parent
        if parent == None:
            self.root = new_node
        elif new_node.val < parent.val:
            parent.left = new_node
        else:
            parent.right = new_node
        
        self._fix_insert(new_node)
        return new_node
    
    def _fix_insert(self, new_node):
        while new_node != self.root and new_node.parent.red:
            if new_node.parent == new_node.parent.parent.right:
                u = new_node.parent.parent.left
                if u.red:
                    u.red = False
                    new_node.parent.red = False
                    new_node.parent.parent.red = True
                    new_node = new_node.parent.parent
                else:
                    if new_node == new_node.parent.left:
                        new_node = new_node.parent
                        self.rotate_right(new_node)
                    new_node.parent.red = False
                    new_node.parent.parent.red = True
                    self.rotate_left(new_node.parent.parent)
            else:
                u = new_node.parent.parent.right
                if u.red:
                    u.red = False
                    new_node.parent.red = False
                    new_node.parent.parent.red = True
                    new_node = new_node.parent.parent
                else:
                    if new_node == new_node.parent.right:
                        new_node = new_node.parent
                        self.rotate_left(new_node)
                    new_node.parent.red = False
                    new_node.parent.parent.red = True
                    self.rotate_right(new_node.parent.parent)
        self.root.red = False
        self.root.parent = self.nil # !!! Do we need this???

    def delete(self, z): # variables names from T.H.Cormen Introduction to algorithms
        self._uncount()
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
                # CASE 2
                if w.left.red == False and w.right.red == False:
                    w.red = True
                    x = x.parent
                # CASE 3
                elif w.right.red == False:
                    w.left.red = False
                    w.red = True
                    self.rotate_right(w)
                    w = x.parent.right
                # CASE 4
                else:
                    w.red = x.parent.red
                    x.parent.red = False
                    w.right.ewd = False
                    self.rotate_left(x.parent)
                    x = self.root
            else:
                w = x.parent.left
                # CASE 1
                if w.red == True:
                    w.red = False
                    x.parent.red = True
                    self.rotate_right(x.parent)
                # CASE 2
                if w.right.red == False and w.left.red == False:
                    w.red = True
                    x = x.parent
                # CASE 3
                elif w.left.red == False:
                    w.right.red = False
                    w.red = True
                    self.rotate_left(w)
                    w = x.parent.left
                # CASE 4
                else:
                    w.red = x.parent.red
                    x.parent.red = False
                    w.left.ewd = False
                    self.rotate_right(x.parent)
                    x = self.root
        x.red = False


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

    def rotate_left(self, node):
        y = node.right
        node.right = y.left
        if y.left != self.nil:
            y.left.parent = node
        
        y.parent = node.parent
        if node.parent == None:
            self.root = y
        elif node == node.parent.left:
            node.parent.left = y
        else:
            node.parent.right = y
        
        y.left = node
        node.parent = y


    def rotate_right(self, node):
        y = node.left
        node.left = y.right
        if y.right != self.nil:
            y.right.parent = node
        
        y.parent = node.parent
        if node.parent == None:
            self.root = y
        elif node == node.parent.right:
            node.parent.right = y
        else:
            node.parent.left = y
        
        y.right = node
        node.parent = y
    
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
