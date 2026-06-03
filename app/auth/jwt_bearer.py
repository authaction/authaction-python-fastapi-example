import os

from authaction import AuthAction
from authaction.fastapi import make_require_auth

aa = AuthAction(
    domain=os.environ["AUTHACTION_DOMAIN"],
    audience=os.environ["AUTHACTION_AUDIENCE"],
)

require_auth = make_require_auth(aa)
