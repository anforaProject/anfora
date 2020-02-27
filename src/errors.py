from starlette.responses import JSONResponse

def DoesNoExist():
    return JSONResponse({"error": "Query didn't find a result"}, status_code=404)

def ValidationError():
    return JSONResponse({"error": "Error validating data"}, status_code=400)

def UserAlreadyExists():
    return JSONResponse({"error": "An user with this username already exists"}, status_code=409)