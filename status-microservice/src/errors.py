from starlette.responses import JSONResponse
from starlette.status import (HTTP_201_CREATED, HTTP_404_NOT_FOUND,
                              HTTP_400_BAD_REQUEST, HTTP_409_CONFLICT,
                              HTTP_503_SERVICE_UNAVAILABLE)


def DoesNoExist():
    return JSONResponse({"error": "Query didn't find a result"}, status_code=HTTP_404_NOT_FOUND)

def ValidationError():
    return JSONResponse({"error": "Error validating data"}, status_code=HTTP_400_BAD_REQUEST)

def ServerError():
    return JSONResponse({"error": "Internal error"}, status_code=HTTP_503_SERVICE_UNAVAILABLE)

def MediaError():
    return JSONResponse({"error": "Media files have been already assigned to an status"}, status_code=HTTP_409_CONFLICT)
