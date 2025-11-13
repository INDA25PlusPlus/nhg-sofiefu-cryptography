import math
import hashlib
# server saves the whole merkle tree whilst client save a constant (root hash)
# both use this class

class Node:
    # n=number of leaf nodes
    n = 8
    tree_depth = math.log2(n) # depth(root_node) = 0
    
    def __init__(self, depth, L, R): 
        self.depth = depth
        self.is_leaf = True if depth==Node.tree_depth else False

        # [L, R] is interval of leaf-node-indices this node covers
        self.L = L 
        self.R = R

        hash = bytes(32)
        left_child = None 
        right_child = None

    def compute_hash(data: bytes):
        return hashlib.sha256(data).digest() # takes bytes and returns 32 bytes

    def update_leaf(self, file_id, new_file: bytes, path_hashes): # leaf nodes are files
        if self.is_leaf:
            self.hash = self.compute_hash(new_file)
            return
        
        mid = (self.L+self.R)//2
        if self.left_child == None:
            self.left_child = Node(self.depth+1, self.L, mid)
        if self.right_child == None:
            self.right_child = Node(self.depth+1, mid+1, self.R)

        # recurse to lower level
        if file_id <= mid:
            path_hashes.append(self.right_child.hash)
            self.left_child.update_leaf(file_id, new_file, path_hashes)
        else:
            path_hashes.append(self.left_child.hash)
            self.right_child.update_leaf(file_id, new_file, path_hashes)
        
        self.hash = self.compute_hash(self.left_child.hash + self.right_child.hash)



# root = Node(depth=0, L=0, R=7)     

