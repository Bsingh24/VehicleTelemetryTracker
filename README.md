# Vehicle Telemetry Tracker
This project utilizes OBD II diagnostic tools in order to retrieve and parse information from a user's vehicle. To do this, `OBD.py` was created to give the user free reign on what data can be retrieved and which they would like to collect. It begins recording data when the user turns on their car and saves the data in a file labeled `CarData.json` once the car is off. An additional file labeled `Logs.json` is also created to store raw commands and responses. Currently PIDs `00-20` and service mode `01` are supported. Additional service modes and PIDs will be added in the future.

# Requirements
* You will need a device to bridge the connection between your vehicle and laptop. You can buy one from various sites such as Walmart, here is a link to one. [OBD II Adapter](https://www.walmart.com/ip/OBDMONSTER-ELM327-USB-FORScan-OBD2-Adapter-F150-F250-Car-Light-Truck-ELMconfig-Scanner-MS-CAN-HS-CAN-Switch-Diagnosis-Windows-V1-5-PIC18F25K80-Chip/769224818?wmlspartner=wlpa&selectedSellerId=101130338&selectedOfferId=A0B75F63BD7845F5B5BED303933303E3&conditionGroupCode=1&veh=seo_fpl&cn=google)
* You will need to install this [CH341SER.EXE](https://www.wch-ic.com/downloads/CH341SER_EXE.html) driver in order to communicate with the device. This is only if you have a **Windows** machine. If you are using Linux, Ubuntu, or MacOS, the driver is preinstalled.
* Create an environment and `pip install -r requirements.txt`. This will download all the necessary libraries and tools you need to run this project.
# Running
You have two options on how you want to run it:
1. Import `OBD.py` and call the functions needed. It will run in the background as you drive and save the information once you are finished. See `mainOBD.py` for reference.
2. If you prefer to see your data being tracked in real time using visualizations, you can run `main.py` by using `fastapi run main.py 127.0.0.1`. You will be able to select what PIDs you want to see and it will display each one on a chart. They only downside is you need internet connection so using your phone as a hotspot may be needed.
# Future Plans
- [ ] Improve the styling of web app
- [ ] Optimize the sampling rate
- [ ] Store previous runs in a database
- [ ] Add ML/DS/DA features
- [ ] Add more PIDs
- [ ] Add more service modes
- [ ] Experiment with CAN bus

Currently this has only been tested on a handful of vehicles. It would be highly appreciated if this could this tested on different vehicles and if you noticed an errors or areas of improvement. Thanks!
| Vehicles Tested |
|    :----:   |
| 2005 Toyota Corolla |
| 2017 Toyota Corolla |
| 2022 Kia K5 | 
