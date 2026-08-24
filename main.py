from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from threading import Thread
from fastapi.responses import FileResponse
from queue import Queue
from OBD import OBD
import asyncio
import time

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
    json_data = await request.json()
    PID = json_data['PIDS']
    print(PID)
    # PID = ['05', '0C', '0D', '0F', '11']
    await asyncio.to_thread(obd.waitCommand)
    return {'status':'success'}


@app.websocket("/ws/trackpids")
async def streamPIDs(websocket: WebSocket):
    await websocket.accept()
    global obd
    global PID
    queue = Queue()

    # def run_generator():
    #     while obd.checkRPM():
    #         for c in PID:
    #             command = '01' + c
    #             result = obd.singleCommand(command)
    #             if result is not None:
    #                 result['pid'] = c
    #                 queue.put(result)
    #             time.sleep(0.25)
    #     print('Engine off...stopping recording..saving data')
    #     obd.COMMAND.saveData()
    #     obd.LOG.saveLogs()
    #     queue.put(None)

    def run_generator():
        FAST_PIDS = {'0C', '0D'}   # RPM, Speed — checked every round
        SLOW_INTERVAL = 3          # seconds between checks for everything else
        last_slow_check = {}

        running = True
        while running:
            now = time.time()
            for c in PID:
                is_fast = c in FAST_PIDS
                due = is_fast or (now - last_slow_check.get(c, 0) >= SLOW_INTERVAL)

                if not due:
                    continue

                command = '01' + c
                result = obd.singleCommand(command)

                if result is not None:
                    result['pid'] = c
                    queue.put(result)

                    if c == '0C' and result['response'] <= 0:
                        running = False   # RPM hit 0 — treat as engine off
                else:
                    if c == '0C':
                        running = False
                        
                if not is_fast:
                    last_slow_check[c] = now

        print('Engine off...stopping recording..saving data')
        obd.COMMAND.saveData()
        obd.LOG.saveLogs()
        queue.put(None)

    thread = Thread(target=run_generator, daemon=True)
    thread.start()
    print('Thread Started')

    try:
        while True:
            result = await asyncio.to_thread(queue.get)
            if result is None:
                break
            await websocket.send_json(result)
    except WebSocketDisconnect:
        print("Client Disconnected")

@app.get("/tracking")
async def tracking_page():
    return FileResponse("templates/tracking.html") 