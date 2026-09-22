from fastapi import HTTPException


async def resolve_path(path: str | None = None, webcode: str | None = None) -> tuple[str, bool]:
    """
    returns a tuple containing the resolved path and a boolean indicating whether the first value is a direct path
    (True) or a webcode (False).
    """

    def exists(param: str | None) -> bool:
        if param is not None and param != "":
            return True
        return False

    if exists(path) == exists(webcode):
        raise HTTPException(status_code=422, detail="Exactly one of 'path' or 'webcode' must be provided.")
    if path:
        return path, True
    if webcode:
        return webcode, False
    return "", False  # unreachable code, but to ensure type checker knows a string is returned
