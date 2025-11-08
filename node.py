import math

class Node:
    # n=number of leaf nodes
    n = 8
    tree_depth = math.log2(n) # depth(root_node) = 0
    
    def __init__(self, depth, L, R): 
        self.depth = depth
        self.is_leaf = True if depth==tree_depth else False

        # [L, R] is interval of leaf-node-indices this node covers
        self.L = L 
        self.R = R

        hash = ""
        left_child = None 
        right_child = None

    def compute_hash():
        hash = 1
        # todo: sha2 - recommended by wikipedia for merkle trees

    def update_leaf(file_id, new_hash, path_nodes): # leaf nodes are files
        if self.is_leaf:
            self.hash = new_hash
            return
        
        mid = (self.L+self.R)//2
        if self.left_child == None:
            self.left_child = Node(self.depth+1, self.L, mid)
        if self.right_child == None:
            self.right_child = Node(self.depth+1, mid+1, self.R)

        # recurse to lower level
        if file_id <= mid:
            path_nodes.append(self.right_child.hash)
            self.left_child.update_leaf(file_id, new_hash, path_nodes)
        else:
            path_nodes.append(self.left_child.hash)
            self.right_child.update_leaf(file_id, new_hash, path_nodes)
        
        self.hash = self.compute_hash(self.left_child.hash + self.right_child.hash)



    


# root = Node(depth=0, L=0, R=7)     

