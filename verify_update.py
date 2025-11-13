# for client: to verify that a file is correctly updated
# run verify_update right after file update 
import hashlib

def compute_hash(data: bytes): 
    return hashlib.sha256(data).digest() # takes bytes and returns 32 bytes

def reconstruct_root_hash(L, R, file_id, depth, path_hashes, leaf_hash):
    if L==R:
        print("LEAF HASH", leaf_hash)
        return leaf_hash
    
    mid = (L+R)//2
    if file_id <= mid:
        left_hash = reconstruct_root_hash(L, mid, file_id, depth+1, path_hashes, leaf_hash)
        right_hash = path_hashes[depth+1]
    else:
        right_hash = reconstruct_root_hash(mid+1, R, file_id, depth+1, path_hashes, leaf_hash)
        left_hash = path_hashes[depth+1]

    hash = compute_hash(left_hash+right_hash)
    print("PATH HASH", depth, hash)
    return hash


def verify_update(file_id, path_hashes, old_root_hash, old_file: bytes, new_file: bytes, n): 
    """
    Verifies after file is updated whether the server has stored it correctly, 
    using nodes along the path to the root to check if the clients stored root hash 
    is the same as the servers
    """
    old_file_hash = compute_hash(old_file)
    new_file_hash = compute_hash(new_file)

    # verify path_hashes by comparing old file resulted root hash with our stored root hash
        
    if old_root_hash != b"":
        computed_old_root_hash = reconstruct_root_hash(0, n-1, file_id, 0, path_hashes, old_file_hash)
        print("COMPUTED old root hash", computed_old_root_hash)
        print("OLD root hash", old_root_hash)
        if computed_old_root_hash != old_root_hash:
            return False # verification failes

    # verify new root hash 
    computed_new_root_hash = reconstruct_root_hash(0, n-1, file_id, 0, path_hashes, new_file_hash)
    if computed_new_root_hash != path_hashes[0]:
        return False

    return path_hashes[0]


