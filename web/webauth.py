from database import db_session
from sqlalchemy import text
import bcrypt
from flask_httpauth import HTTPBasicAuth

auth = HTTPBasicAuth()


@auth.verify_password
def verify_password(username, password):
    result = db_session.execute(text(
        "Select Password from vault.Users where UserName=:id"
    ), {"id": username}).fetchone()
    if result is None or len(result) == 0:
        return None
    else:
        if bcrypt.checkpw(str(password).encode(), str(result[0]).encode()):
            return username
    return None
