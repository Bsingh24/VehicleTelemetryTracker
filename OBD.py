import serial
import serial.tools.list_ports
import time
import json
from datetime import datetime
from Help import Help

# Log all commands and responses given
# Need to add Database compatability
class Log: 
    def __init__(self):
        self.RESPONSE_LOG = []

    def saveLogs(self, filename='Logs.json'):
        with open(filename, 'w') as f:
            json.dump(self.RESPONSE_LOG, f)
        print(f'Logs saved in {filename}')

    def logResponse(self, command, response):
        self.RESPONSE_LOG.append(
            {"Time":str(datetime.now()),
             "Command": command,
             "Response": response}
        )

    def printLogs(self):
        for i, log in enumerate(self.RESPONSE_LOG):
            print(f'Item: {i + 1}')
            for k, v in log.items():
                print(f"{k}: {v}")
            print("-------------------------------")

# Finds and lists all available ports - user selects a port based on results
class Ports:
    def __init__(self):
        self.PORTS = None
    
    def findPorts(self):
        self.PORTS = serial.tools.list_ports.comports()

    def listDevices(self):
        for i, p in enumerate(self.PORTS):
            print('-----------------------------')
            print(f'Device: {i}')
            print(f'Device Name: {p.device}')
            print(f'Device Vendor ID: {p.vid}')
            print(f'Device Product ID: {p.pid}')
            # print(f'Device Serial Number: {p.serial_number}')
            print('-----------------------------')
      
# Initializes connection to OBD device, startup commands, and protocol used by vehicle for quicker retrieval
class Initialize:
    def __init__(self, port, index, baudrate=38400, timeout=2):
        self.PROTOCOL = None
        self.DEVICE = serial.Serial(
            port=port[index].device,
            baudrate=baudrate,
            parity=serial.PARITY_NONE,
            stopbits=serial.STOPBITS_ONE,
            bytesize=serial.EIGHTBITS,
            timeout=timeout
        )
    
    def initCommand(self, LOG, COMMANDS=['ATZ','ATE0', 'ATL0', 'ATSP0', 'ATH0', '0100', 'ATDPN']):
        COMMANDS = COMMANDS
        SLEEP = {'ATZ': 1.5, '0100':10}
        for c in COMMANDS:
            self.DEVICE.reset_input_buffer()
            self.DEVICE.write((c + "\r").encode())
            time.sleep(SLEEP.get(c, 0.5))
            response = self.DEVICE.read(self.DEVICE.in_waiting).decode(errors="ignore").replace('\r', '').replace('>','').strip()
            LOG.logResponse(c, response) 
            
        self.PROTOCOL = f"ATSP{response[1]}"
        
        self.DEVICE.reset_input_buffer()
        self.DEVICE.write((self.PROTOCOL + "\r").encode())
        time.sleep(0.5)
        response = self.DEVICE.read(self.DEVICE.in_waiting).decode(errors="ignore").replace('\r', '').replace('>','').strip()
        LOG.logResponse(self.PROTOCOL, response)

# Discovers what ports you are able to observe and collect data from
class Support:
    def __init__(self, DEVICE, LOG):
        self.DEVICE = DEVICE
        self.LOG = LOG

    def supportedPIDs(self):
        PID = ['0100', '0120', '0140']
        supported_PIDs = []
        for p in PID:
            self.DEVICE.write((p + "\r").encode())
            time.sleep(2)
            response = self.DEVICE.read(self.DEVICE.in_waiting).decode(errors="ignore").strip()
            response = response.replace(">", "")
            response = response.split("\r")
            init_PID = [l.strip() for l in response if l.strip() and "SEARCHING" not in l and "NO DATA" not in l]
            if not init_PID:
                continue
            clean_PID = init_PID[0]
            self.LOG.logResponse(p, clean_PID)
            supported_PIDs.append(clean_PID)
        return supported_PIDs
    
# Converts data from OBD to appropriate value
class Conversion:
    def hextoBinary(self, hex):
        hex_arr = hex.split(" ")
        binary_arr = []
        for i in range(2, len(hex_arr)):
           binary_arr.append(bin(int(hex_arr[i], 16))[2:].zfill(8))
        return binary_arr
    
    def decimaltoHex(self, n):
        return hex(n)[2:].upper().zfill(2)

# Tracks data and converts them to readable value
# At the moment tracks certain values for testing purposes
class Command:
    def __init__(self):
        self.CAR_LOG = {'Time': [],
                        'Engine Coolant Temp': [],
                        'Short Term Fuel Trim (STFT)': [],
                        'Long Term Fuel Trim (LTFT)': [],
                        'Engine Speed': [],
                        'Vehicle Speed': [],
                        'Timing Advance': [],
                        'Intake Air Temp': [],
                        'MAF Sensor Air Flow Rate': [],
                        'Throttle Position': [],
                        'O2 Sensor (Voltage with STFT)': [],
                        'O2 Sensor (Air-Fuel Ratio with Voltage)': []}
           
        self.FUNCTIONS = {'05': self.EngineCoolantTemp,
                          '06': self.STFT,
                          '07': self.LTFT,
                          '0C': self.EngineSpeed,
                          '0D': self.VehicleSpeed,
                          '0E': self.TimingAdvance,
                          '0F': self.IntakeAirTemp,
                          '10': self.MAFAirFlowRate,
                          '11': self.ThrottlePosition,
                          '15': self.O2SensorSTFT,
                          '24': self.O2SensorAirFuelRatio}
        
    def saveData(self, filename='CarData.json'):
        with open(filename, 'w') as f:
            json.dump(self.CAR_LOG, f)
        print(f'Logs saved in {filename}')
        
    def HextoDecimal(self, hex):
        return int(hex, 16)
        
    def EngineCoolantTemp(self, response):
        response = response.split(' ')
        A = self.HextoDecimal(response[2])
        ECoolantTemp = A - 40
        self.CAR_LOG['Engine Coolant Temp'].append(ECoolantTemp)
        return ECoolantTemp

    def STFT(self, response):
        response = response.split(' ')
        A = self.HextoDecimal(response[2])
        SFT = (100/128) * A - 100
        self.CAR_LOG['Short Term Fuel Trim (STFT)'].append(SFT)
        return SFT

    def LTFT(self, response):
        response = response.split(' ')
        A = self.HextoDecimal(response[2])
        LFT = (100/128) * A - 100
        self.CAR_LOG['Long Term Fuel Trim (LTFT)'].append(LFT)
        return LFT

    def EngineSpeed(self, response):
        response = response.split(' ')
        A = self.HextoDecimal(response[2])
        B = self.HextoDecimal(response[3])
        ESpeed = ((256 * A) + B) / 4
        self.CAR_LOG['Engine Speed'].append(ESpeed)
        return ESpeed
    
    def VehicleSpeed(self, response):
        response = response.split(' ')
        VSpeed = self.HextoDecimal(response[2])
        self.CAR_LOG['Vehicle Speed'].append(VSpeed)
        return VSpeed

    def TimingAdvance(self, response):
        response = response.split(' ')
        A = self.HextoDecimal(response[2])
        Timing = (A/2) - 64
        self.CAR_LOG['Timing Advance'].append(Timing)
        return Timing

    def IntakeAirTemp(self, response):
        response = response.split(' ')
        A = self.HextoDecimal(response[2])
        IntakeTemp = A - 40
        self.CAR_LOG['Intake Air Temp'].append(IntakeTemp)
        return IntakeTemp

    def MAFAirFlowRate(self, response):
        response = response.split(' ')
        A = self.HextoDecimal(response[2])
        B = self.HextoDecimal(response[3])
        MAFRate = ((256 * A) + B) / 100
        self.CAR_LOG['MAF Sensor Air Flow Rate'].append(MAFRate)
        return MAFRate

    def ThrottlePosition(self, response):
        response = response.split(' ')
        A = self.HextoDecimal(response[2])
        Throttle = (100 / 255) * A
        self.CAR_LOG['Throttle Position'].append(Throttle)
        return Throttle

    def O2SensorSTFT(self, response):
        response = response.split(' ')
        A = self.HextoDecimal(response[2])
        Voltage = A / 200
        if response[3] == 'FF':
            SFT = None
        else:
            B = self.HextoDecimal(response[3])
            SFT = (100 / 128) * B - 100
        self.CAR_LOG['O2 Sensor (Voltage with STFT)'].append((Voltage, SFT))
        return [Voltage, SFT]

    def O2SensorAirFuelRatio(self, response):
        response = response.split(' ')
        A = self.HextoDecimal(response[2])
        B = self.HextoDecimal(response[3])
        C = self.HextoDecimal(response[4])
        D = self.HextoDecimal(response[5])
        AFRatio = (2 / 65536) * (256 * A + B)
        Voltage = (8 / 65536) * (256 * C + D)
        self.CAR_LOG['O2 Sensor (Air-Fuel Ratio with Voltage)'].append((AFRatio, Voltage))
        return [AFRatio, Voltage]


# Main class operating everything - user communicates with this class
class OBD:
    def __init__(self):
        self.LOG = Log()
        self.PORTS = Ports()
        self.PORTS.findPorts()
        # self.PORTS.listDevices()
        self.DEVICE = None
        self.CONVERT = Conversion()
        self.HELP = Help()
        self.COMMAND = Command()

    def connect(self, index):
        self.PORT_INDEX = index
        init = Initialize(self.PORTS.PORTS, index)
        self.DEVICE = init.DEVICE
        init.initCommand(self.LOG)
        self.PROTOCOL = init.PROTOCOL
        print(f"Established connection with device: {self.PORTS.PORTS[self.PORT_INDEX].device} ({self.PORT_INDEX})")

    def supportedPIDs(self):
        ignore = ['00', '20', '40']
        if not self.DEVICE:
            print('-----------------------------')
            print("Device needs to be connected")
            print('-----------------------------')

        else:
            support = Support(self.DEVICE, self.LOG)
            supportedPIDs = support.supportedPIDs()
            PIDList = []
            if supportedPIDs:
                n = 0
                print('-----------------------------')
                print('Supported PIDs:')
                print('-----------------------------')
                for p in supportedPIDs:
                    binary = self.CONVERT.hextoBinary(p)
                    for b in binary:
                        for i in range(len(b)):
                            n += 1
                            HEX = self.CONVERT.decimaltoHex(n)
                            if HEX not in ignore and b[i] == '1':
                                PIDList.append((HEX, self.HELP.PortID[HEX]))
                            if b[i] == '1':
                                print(f'Port {HEX}: {self.HELP.PortID[HEX]}')
                return PIDList
            else:
                print('No Supported PIDs')
                    
    def checkRPM(self, command='010C'):
        try:
            self.DEVICE.reset_input_buffer()
            self.DEVICE.write((command + "\r").encode())
            time.sleep(0.5)
            response = self.DEVICE.read(self.DEVICE.in_waiting).decode(errors='ignore').replace('\r', '').replace('>', '').strip()
            split_response = response.split()
            A = self.COMMAND.HextoDecimal(split_response[2])
            B = self.COMMAND.HextoDecimal(split_response[3])
            RPM = ((256 * A) + B) / 4
            return RPM > 0
        except Exception:
            return False
   
    def waitCommand(self, command='010C'):
        while True:
            if self.checkRPM():
                print('Logging Data...')
                break
            time.sleep(2)
    
    def sendCommand(self, commands):
        while self.checkRPM():
            timestamp = str(datetime.now())
            self.COMMAND.CAR_LOG['Time'].append(timestamp)
            for command in commands:
                try:
                    self.DEVICE.reset_input_buffer()
                    self.DEVICE.write((command + "\r").encode())
                    time.sleep(0.25)
                    response = self.DEVICE.read(self.DEVICE.in_waiting).decode(errors="ignore").replace('\r', '').replace('>', '').strip()
                    split_response = response.split(' ')
                    if len(split_response) > 2 and split_response[1] in self.COMMAND.FUNCTIONS:
                        self.COMMAND.FUNCTIONS[split_response[1]](response)
                    self.LOG.logResponse(command, response)
                except Exception as e:
                    print(f'Error on command: {command}: {e}')
                    break
        print('Engine off...stopping recording..saving data')
        self.COMMAND.saveData()
        self.LOG.saveLogs()

    def singleCommand(self, command):
        try:
            self.DEVICE.reset_input_buffer()
            self.DEVICE.write((command + "\r").encode())
            time.sleep(0.25)
            response = self.DEVICE.read(self.DEVICE.in_waiting).decode(errors="ignore").replace('\r', '').replace('>', '').strip()
            split_response = response.split(' ')
            if len(split_response) > 2 and split_response[1] in self.COMMAND.FUNCTIONS:
                res = self.COMMAND.FUNCTIONS[split_response[1]](response)
                self.LOG.logResponse(command, response)
                return {'command': command, 'response': res, 'timestamp':str(datetime.now())}
                
        except Exception as e:
            print(f'Error on command: {command}: {e}')
            return None