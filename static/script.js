// import collectbuttonclick from "../static/button.js";
var socket = io.connect('http://' + document.domain + ':' + location.port);
var isConnected = false;

socket.on('data_from_device', function(data) {
    document.getElementById('currentrotationalspeed').innerText = data.currentrotationalspeed.toFixed(2);
    document.getElementById('setrotationalspeed').innerText = data.setrotationalspeed.toFixed(2);
    document.getElementById('targetrotationalspeed').innerText = data.targetrotationalspeed.toFixed(2);
    document.getElementById('faultinformation').innerText = data.faultinformation.toFixed(2);
    document.getElementById('dcbusvoltage').innerText = data.dcbusvoltage.toFixed(2);
    document.getElementById('uphasecurrent').innerText = data.uphasecurrent.toFixed(2);
    document.getElementById('power').innerText = data.power.toFixed(2);
    document.getElementById('dissipativeresistance').innerText = data.dissipativeresistance.toFixed(2);
    document.getElementById('daxieinductor').innerText = data.daxieinductor.toFixed(2);
    document.getElementById('qaxieinductor').innerText = data.qaxieinductor.toFixed(2);
    document.getElementById('reverseemfconstant').innerText = data.reverseemfconstant.toFixed(2);
    document.getElementById('polaritylog').innerText = data.polaritylog.toFixed(2);
    document.getElementById('motorinputpower').innerText = data.motorinputpower.toFixed(2);
    document.getElementById('torque').innerText = data.torque.toFixed(2);
    document.getElementById('motoroutputpower').innerText = data.motoroutputpower.toFixed(2);
    document.getElementById('addload').innerText = data.addload.toFixed(2);
    document.getElementById('speedcompensationcoefficient').innerText = data.speedcompensationcoefficient.toFixed(2);
    document.getElementById('currentbandwidth').innerText = data.currentbandwidth.toFixed(2);
    document.getElementById('observercompensationcoefficient').innerText = data.observercompensationcoefficient.toFixed(2);
    document.getElementById('load').innerText = data.load.toFixed(2);
    document.getElementById('speed').innerText = data.speed.toFixed(2);

    if (data.faultinformation != 0)
        document.getElementById('faultinformation').innerText = "故障";
    else document.getElementById('faultinformation').innerText = "良好";
});

socket.on('connection', function(devicestatus) {
    if (devicestatus.status == true) {
        isConnected = true;
        document.getElementById('status').innerText = "已连接";
        document.getElementById('connect_button').innerText = '断开连接';
        var button = document.getElementById('start_button');
        button.disabled = false;
        var button = document.getElementById('stop_button');
        button.disabled = false;
    } else {
        isConnected = false;
        document.getElementById('status').innerText = "未连接";
        document.getElementById('connect_button').innerText = '连接设备';
        var button = document.getElementById('start_button');
        button.disabled = true;
        var button = document.getElementById('stop_button');
        button.disabled = true;

    }
});


window.onload = function() {
    // document.getElementById('connect_button').addEventListener('click', connectDevice);

    document.getElementById('start_button').addEventListener('click', function() {
        socket.emit('start_data');
    });

    document.getElementById('stop_button').addEventListener('click', function() {
        socket.emit('stop_data');
    });
    
}


