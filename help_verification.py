# for server: when received verify_update from client, run this function


def update_file(file_id, new_hash): # updates file and sends back nodes along the path to this leaf-node
    path_nodes.append(root.hash)
    root.query(file_id, new_hash, path_nodes)


    # send path_nodes to client
    return path_nodes