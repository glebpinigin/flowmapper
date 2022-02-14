class AbstractBSTData():
    def set_node(self, node):
        self.node = node
    
    def unpack(self):
        return None
    
    def __gt__(self, other):
        return self.unpack() > other
        
    def __lt__(self, other):
        return self.unpack() < other
    
    def __ge__(self, other):
        return self.unpack() >= other
    
    def __le__(self, other):
        return self.unpack() <= other


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
        self.nil = SearchTreeNode(0)
        self.root = self.nil
    
    
    def insert(self, val, rt=False):
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
                current = current.lef
            elif new_node.val > current.val:
                current = current.right
            else:
                raise Warning("equal data in nodes")
        
        new_node.parent = parent
        if parent == None:
            self.root = new_npde
        elif new_node.val < parent.val:
            parent.left = new_node
        else:
            parent.right = new_node
        
        self.fix_insert(new_node)
            if rt:
                return new_node
    
    
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
    
    
    def fix_insert(self, new_node):
        while new_node != self.root and new_node.parent.red:
            if new_node.parent == new_node.parent.parent.right:
                u = new_node.parent.parent.left
                if u.red:
                    u.ref = False
                    new_node.parent.red = False
                    new_node.paren.parent.red = True
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
                    u.ref = False
                    new_node.parent.red = False
                    new_node.paren.parent.red = True
                    new_node = new_node.parent.parent
                else:
                    if new_node == new_node.parent.right:
                        new_node = new_node.parent
                        self.rotate_left(new_node)
                    new_node.parent.red = False
                    new_node.parent.parent.red = True
                    self.rotate_right(new_node.parent.parent)