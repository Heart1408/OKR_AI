from typing import Annotated
from src.base.config import get_config
from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import JSONResponse
import jwt
from jwt.exceptions import InvalidTokenError

def error_response(error_msg: str, status_code: int) -> JSONResponse:
    """
    Logs the error message and returns a JSONResponse with the error message.

    Args:
        error_msg (str): the error message to be logged and returned in the JSONResponse
        status_code (int): the HTTP status code

    Returns:
        JSONResponse: JSONResponse containing the error message
    """
    return JSONResponse(
        content={"error": {"message": error_msg}},
        status_code=status_code,
    )


def validate_token(token: str):
    """
    Validate a JWT token using the Azure AD JWKS endpoint.

    Args:
        token (str): The JWT token to be validated.

    Returns:
        ``{status: bool, message: str}``
        status: True if the token is valid, False otherwise.
        message: respone content.
    """
    signing_key = token 
    if not signing_key:
        return { "status": False, "message": "Empty token"}
    
    SECRET_KEY = get_config("SECRET_KEY")
    ALGORITHM = get_config("ALGORITHM")
    try:
        payload = jwt.decode(jwt=signing_key.strip(), key=SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            return { "status": False, "message": "Cannot find right properties"}
        return { "status": True, "message": "Found it"}
    except InvalidTokenError as e:
        return { "status": False, "message": "InvalidTokenError"}
