from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from threading import Thread
from fastapi.responses import FileResponse
from queue import Queue
from OBD import OBD
import asyncio

obd = None
PID = None
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get('/')
def main(request: Request):
    return templates.TemplateResponse(request, 'index.html', {})

@app.get('/initialize')
def initialize():
    global obd
    obd = OBD()
    if obd.PORTS.PORTS:
        ports = {}
        for i, p in enumerate(obd.PORTS.PORTS):
            ports[i] = p.device
        return {'success': True, 'ports': ports}
    else:
        return {'success': False}

@app.post('/portConnection')
async def connectPort(request: Request):
    global obd
    json_data = await request.json()
    selected_port = int(json_data["selected_port"])
    obd.connect(selected_port)
    PIDList = obd.supportedPIDs()
    return {'device': obd.PORTS.PORTS[selected_port], 'PIDList': PIDList}
        
@app.post('/trackpids')
async def trackPIDs(request: Request):
    global obd
    global PID
    # json_data = await request.json()
    # PID = json_data['PIDS']
    PID = ['05', '0C', '0D', '0F', '11']
    await asyncio.to_thread(obd.waitCommand())
    return {'status':'success'}


@app.websocket("/ws/trackpids")
async def streamPIDs(websocket: WebSocket):
    await websocket.accept()
    global obd
    global PID
    queue = Queue()

    def run_generator():
        while obd.checkRPM():
            for c in PID:
                command = '01' + c
                result = obd.singleCommand(command)
                if result is not None:
                    result['pid'] = c
                    queue.put(result)
        print('Engine off...stopping recording..saving data')
        obd.COMMAND.saveData()
        obd.LOG.saveLogs()
        queue.put(None)

    thread = Thread(target=run_generator, daemon=True)
    thread.start()

    try:
        while True:
            result = queue.get()
            if result is None:
                break
            await websocket.send_json(result)
    except WebSocketDisconnect:
        print("Client Disconnected")

@app.get("/tracking")
async def tracking_page():
    return FileResponse("tracking.html") 