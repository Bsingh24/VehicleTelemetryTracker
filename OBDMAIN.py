from OBD import OBD
import time

obd = OBD()
obd.connect(0)
obd.supportedPIDs()
obd.waitCommand()
count = 0
start_total = time.time()

while True:
    start = time.time()
    result = obd.singleCommand('010C')
    elapsed = time.time() - start
    if result is None:
        break
    count += 1
    print(f"#{count} | took {elapsed*1000:.1f}ms | result: {result}")

    if count % 50 == 0:
        avg = (time.time() - start_total) / count
        print(f"--- Average: {avg*1000:.1f}ms/call, ~{1/avg:.1f} calls/sec ---")

print('STOPPED')