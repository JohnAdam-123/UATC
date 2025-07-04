import hashlib
import os

def hash_password(password, salt=None):
    if salt is None:
        salt = os.urandom(16).hex()
    hash_obj = hashlib.sha256((password + salt).encode('utf-8'))
    return hash_obj.hexdigest(), salt

def verify_hash(password, stored_hash, stored_salt):
    calculated_hash, _ = hash_password(password, stored_salt)
    return calculated_hash == stored_hash
