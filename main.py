from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from threading import Thread
from fastapi.responses import RedirectResponse
from queue import Queue
from OBD import OBD

obd = None
PID = None
# tracking_status = 'idle'
app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


@app.get('/')
def main(request: Request):
    return templates.TemplateResponse(request, 'indexalt.html', {})

@app.get('/initialize')
def initialize():
    global obd
    obd = OBD()
    # if obd.PORTS.PORTS:
    return {'success': True, 'ports': {0:'yes', 1:'no', 2:'maybe'}} # TO DO
    # else:
        # return {'success': False}

@app.post('/portConnection')
async def connectPort(request: Request):
    global obd
    json_data = await request.json()
    # selected_port = int(json_data["selected_port"])
    # obd.connect(selected_port)
    # PIDList = obd.supportedPIDs()
    # return {'device': obd.PORTS.PORTS[selected_port], 'PIDList': PIDList}
    return {'device': 0, 'PIDList': [('11', 'Port A'), ('12', 'Port B')]}
        
@app.post('/trackpids')
async def trackPIDs(request: Request):
    global obd
    global PID
    json_data = await request.json()
    PID = json_data['PIDS']
    # obd.waitCommand()
    return {'status':'success'}


@app.websocket("/ws/trackpids")
async def streamPIDs(websocket: WebSocket):
    await websocket.accept()
    global obd
    global PID
    queue = Queue()

    def run_generator():
        for result in obd.sendCommand(PID):
            queue.put(result)
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