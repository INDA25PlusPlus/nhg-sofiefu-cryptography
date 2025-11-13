import math
import hashlib
# server saves the whole merkle tree whilst client save a constant (root hash)
# both use this class

class Node:
    # n=number of leaf nodes
    n = 8
    tree_depth = int(math.log2(n)) # depth(root_node) = 0
    
    def __init__(self, depth, L, R): 
        self.depth = depth
        self.is_leaf = True if depth==Node.tree_depth else False

        # [L, R] is interval of leaf-node-indices this node covers
        self.L = L 
        self.R = R

        self.hash = bytes(32)
        self.left_child = None 
        self.right_child = None

    def compute_hash(self, data: bytes):
        return hashlib.sha256(data).digest() # takes bytes and returns 32 bytes

    def update_leaf(self, file_id, encrypted_file, path_hashes): # leaf nodes are files
        if self.left is None and self.right is None:
            # leaf node
            if self.file_id == file_id:
                self.hash = sha256(encrypted_file)
            # return path
            return
        # descend
        mid = (self.start + self.end) // 2
        if file_id <= mid:
            self.left.update_leaf(file_id, encrypted_file, path_hashes)
            direction = "R"
            sibling_hash = self.right.hash
        else:
            self.right.update_leaf(file_id, encrypted_file, path_hashes)
            direction = "L"
            sibling_hash = self.left.hash

        # record sibling and direction for verification later
        path_hashes.append((sibling_hash, direction))

        # recompute current node hash
        self.hash = sha256(self.left.hash + self.right.hash)



# root = Node(depth=0, L=0, R=7)     

