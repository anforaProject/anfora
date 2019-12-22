from starlette.responses import JSONResponse

async def pipe_request(request, method_response:JSONResponse) -> JSONResponse:

    """
    Given a request return correct body response and status code

    """
    return JSONResponse(status_code=request.status, content = await request.json())
    
