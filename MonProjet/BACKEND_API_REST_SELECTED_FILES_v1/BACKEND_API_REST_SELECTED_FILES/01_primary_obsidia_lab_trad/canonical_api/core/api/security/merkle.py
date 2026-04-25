import hashlib
import json
import os

def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()

def compute_merkle_root(file_path: str) -> str:
    if not os.path.exists(file_path):
        return None

    with open(file_path, "rb") as f:
        leaves = [sha256(line.strip()) for line in f if line.strip()]

    if not leaves:
        return None

    while len(leaves) > 1:
        if len(leaves) % 2 == 1:
            leaves.append(leaves[-1])

        new_level = []
        for i in range(0, len(leaves), 2):
            combined = (leaves[i] + leaves[i+1]).encode()
            new_level.append(sha256(combined))
        leaves = new_level

    return leaves[0]
