import json
from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.responses import StreamingResponse
from typing import Union
from .robot_move_control import move_forward, stop_motors, turn, distance
from pydantic import BaseModel
import asyncio
import random

flag = False 

app = FastAPI()

class Operation(BaseModel):
    """Send data from client using a request body like distance or degrees and the API returns a response body"""
    duration: Union[int, None] = None
    degrees: Union[int, None] = None

# duration and 0 degrees = forward, degrees positive = right , degrees negative = left 

@app.post("/move")
async def move(operation: Operation, background_tasks: BackgroundTasks):
    """
## This endpoint is moving the robot forward for x seconds or turning it for y degrees.

### Inputs Required

- **duration**: Input an integer number.
- **degrees**: Input an integer number.

### Example
- Possible combinations: '{"duration": Int, "degrees": 0}', '{"duration": 0, "degrees": 0}', '{"duration": 0, "degrees": Int or -Int}'
    """
    global flag
    flag = True
    if operation.degrees == 0 and operation.duration == 0:
        operation.duration = None
        background_tasks.add_task(move_forward,operation.duration)
        return {"message": "Robot moving forward until you stop the motors"}
    elif operation.degrees == 0 and operation.duration is not None:
        background_tasks.add_task(move_forward, operation.duration)
        return {"message": f"Robot moving forward for {operation.duration} seconds successfully."}
        
    elif operation.duration is not 0 and operation.degrees is not 0:
        raise HTTPException(status_code=400, detail="duration must be 0 if you want to input degrees")
    
    else:
        task = asyncio.create_task(turn(operation.degrees))
        await task
        flag = False
        if operation.degrees > 0:
            return {"message": f"Robot turned {operation.degrees} degrees right successfully."}
        else:
            return {"message": f"Robot turned {operation.degrees} degrees left successfully."}
        






async def sonar_loop():
    global flag
    while flag == False:
        dist = distance()
        if dist > 20:
           move_forward() 
           await asyncio.sleep(0.01)
        else:
            random_angle = random.choice([-90, 90])
            stop_motors()
            task = asyncio.create_task(turn(random_angle))
            await task
            await asyncio.sleep(0.3)

@app.post("/move/sonar")
async def obastacle_avoidance(sonar_task: BackgroundTasks):
    """
## This endpoint starts the obstacle avoidance algorithm 

"""
    global flag
    flag = False
    sonar_task.add_task(sonar_loop)
    return {"message": "Robot movement with obstacle avoidance started."}
        


@app.post("/stop")
async def stop():
    """
    ## This endpoint stops all the functionalities of the robot 


    """
    global flag
    flag = True
    stop_motors()
    return {"message": "Robot stopped successfully."}
# End




#Sonar measurements using Server-Sent Events(SSE) 


async def generate_sse():
    while True:
        dist = distance()
        data = {"distance": round(dist,1)}
        yield f"data: {json.dumps(data)}\n\n"
        await asyncio.sleep(1)


@app.post("/distance/sonar")
async def sonar():
    """
    ## This endpoint uses the sonar sensor to measure the distance from an object.

    """
    mes = StreamingResponse(generate_sse(), media_type="text/event-stream")
    mes.headers["Cache-Control"] = "no-cache"
    mes.headers["Connection"] = "keep-alive"
    return mes
# End 


### Docs Custom ###
from fastapi.openapi.utils import get_openapi

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="5G Driving Robot",
        version="2.5.0",
        description="",
        routes=app.routes,
    )
    openapi_schema["info"]["x-logo"] = {
        "url": "https://fastapi.tiangolo.com/img/logo-margin/logo-teal.png"
        
    }
    openapi_schema["paths"]["/move"]["post"]["x-codeSamples"] = [{
    'lang': 'Curl',
    'source': "curl -X POST -H 'Content-Type: application/json' -d '{\"duration\": 4, \"degrees\": 0}' http://10.160.1.133:5001/move",
    'label': 'Terminal'
}]
    openapi_schema["paths"]["/move/sonar"]["post"]["x-codeSamples"] = [{
    'lang': 'Curl',
    'source': 'curl -X POST http://10.160.1.133:5001/move/sonar',
    'label': 'Terminal'
}]
    openapi_schema["paths"]["/stop"]["post"]["x-codeSamples"] = [{
    'lang': 'Curl',
    'source': 'curl -X POST http://10.160.1.133:5001/stop',
    'label': 'Terminal'
}]
    openapi_schema["paths"]["/distance/sonar"]["post"]["x-codeSamples"] = [{
    'lang': 'Curl',
    'source': "curl -X POST http://10.160.1.133:5001/distance/sonar",
    'label': 'Terminal'
}]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi
