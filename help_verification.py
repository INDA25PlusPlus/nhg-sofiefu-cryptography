# the server saves the whole merkle tree whilst client save a constant (root hash)


def update_file(file_id, new_hash): # updates file and sends back nodes along the path to this leaf-node
    path_nodes.append(root.hash)
    root.query(file_id, new_hash, path_nodes)


    # send path_nodes to client