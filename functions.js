async function buttonClick() {
    const response = await fetch("/initialize");
    const data = await response.json();
    const buttoninitial = document.getElementById('initialbutton');
    if (data.success === true) {
        document.getElementById('buttoncheck').innerText = "Devices found!";
        const list = document.getElementById('list');
        const connectButton = document.getElementById('connectbutton');
        list.innerHTML = "";

        const option = document.createElement('option');
        option.textContent = "--";
        list.appendChild(option);
        for (const key in data.ports) {
            const option = document.createElement('option');
            option.value = key;
            option.textContent = data.ports[key];
            list.appendChild(option);
        }
        list.style.display = "inline-block";
        connectButton.style.display = "inline-block";
        buttoninitial.style.display = "none";

    }
    else {
        document.getElementById('buttoncheck').innerText = "No devices found, please check devices and if vehicle is on..."
    }
}

async function connectToPort() {
   const port = document.getElementById("list");
   const portValue = port.value;
   const connectButton = document.getElementById('connectbutton');

   const response = await fetch("/portConnection", {
        method: "POST",
        headers: {"Content-Type": "application/json"},
        body: JSON.stringify({selected_port: portValue})});

    const data = await response.json();
    console.log(data);
    document.getElementById('buttoncheck').innerText = `Connected with device ${data.device.name} (${portValue})`;
    connectButton.style.display="none";
    port.style.display="none";
    // print list of ports available to view
    const pid = document.getElementById("PIDOptionsList");
    const selectAllButton = document.getElementById("selectallbutton");
    const clearButton = document.getElementById("clearbutton");
    // const br = document.createElement('br');
    // pid.append(br);
    selectAllButton.style.display='inline-block';
    clearButton.style.display='inline-block';
    for (let i = 0; i < data.PIDList.length; i++) {
        const label = document.createElement('label');
        label.style.display = 'block';
        label.innerHTML = `<input type="checkbox" value="${data.PIDList[i][0]}"> ${data.PIDList[i][0]} - ${data.PIDList[i][1]}`;
        pid.appendChild(label);
    }
    const submit = document.getElementById("submitPID");
    submit.style.display='block';
}

async function PIDSubmission(n) {
    const pid = document.getElementById("PIDOptionsList");
    const inputs = pid.querySelectorAll("input");
    console.log(inputs);
    if (n == 0) {
        for (let i = 0; i < inputs.length; i++) {
            inputs[i].checked = false;  
        }
    }
    else if (n == 1) {
        for (let i = 0; i < inputs.length; i++) {
            inputs[i].checked = true;  
        }
    }
    else {
        const SELECTED_PIDS = [];
        for (let i = 0; i < inputs.length; i++) {
            if (inputs[i].checked) {
                SELECTED_PIDS.push(inputs[i].value);
            }
        }
        const response = await fetch("/trackpids", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({PIDS: SELECTED_PIDS})});
        
        const data = await response.json();
        console.log(data)

        const pidsParam = encodeURIComponent(SELECTED_PIDS.join(','));
        window.location.href = `/tracking?pids=${pidsParam}`;
    }
}