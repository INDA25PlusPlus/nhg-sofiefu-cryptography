# for client: to verify that files is correctly updated
# run verify_update right after file update 
import hashlib

def compute_hash(data):
    return hashlib.sha256(data).hexdigest()

def reconstruct_root_hash(L, R, file_id, depth, path_nodes, leaf_hash):
    if L==R:
        return leaf_hash
    
    mid = (L+R)//2
    hash = ""
    if file_id <= mid:
        hash = reconstruct_root_hash(L, mid, file_id, path_nodes, leaf_hash)
        return compute_hash(hash + path_nodes[depth])
    else:
        hash = reconstruct_root_hash(mid+1, R, file_id, path_nodes, leaf_hash)
        return compute_hash(path_nodes[depth] + hash)


def verify_update(file_id, path_nodes, old_root_hash, new_hash): # after update it requests nodes along the path to the root, to verify

    # recursively walk down in binary tree to verify old root-hash with complemented path nodes
    computed_old_root_hash = reconstruct_root_hash(0, n-1, file_id, 0, path_nodes, old_root_hash)
    if (computed_old_root_hash != path_nodes[0]) or (computed_old_root_hash != old_root_hash): # verifies computedroot=claimedroot=realroot
        return False # verification failes

    # verify new root hash 
    computed_new_root_hash = reconstruct_root_hash(0, n-1, file_id, 0, path_nodes, old_root_hash)
    if computed_new_root_hash != root_hash:
        return False

    return True


