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
            val.set_node(self)
        else:
            raise ValueError("data must be enharited from AbstractBSTData")
        self.left = None
        self.right = None


class AbstractSearchTree:
    
    def __init__(self):
        """Red-Black binary search tree"""
        self.nil = SearchTreeNode(AbstractBSTData())
        self.nil.red = False
        self.nil.left = None
        self.nil.right = None
        self.root = self.nil
    
    
    def insert(self, val):
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
            elif new_node.val >= current.val:
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
        
        self.fix_insert(new_node)
        return new_node
    
    def fix_insert(self, new_node):
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
