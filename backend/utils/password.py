import bcrypt
def hash_password(password: str) -> str:
    """加密"""
    hash_pw = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
    return hash_pw
def verify_password(password:str, hashed_password:str) -> bool:
    """验证"""
    res = bcrypt.checkpw(password.encode("utf-8"), hashed_password.encode("utf-8"))
    return res