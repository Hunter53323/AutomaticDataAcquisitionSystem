// import collectbuttonclick from "../static/button.js";
var socket = io.connect('http://' + document.domain + ':' + location.port);
var isConnected = false;

socket.on('data_from_device', function(data) {
    document.getElementById('currentrotationalspeed').innerText = data.实际转速.toFixed(2);
    document.getElementById('setrotationalspeed').innerText = data.设定转速.toFixed(2);
    document.getElementById('targetrotationalspeed').innerText = data.目标转速.toFixed(2);
    // document.getElementById('dcbusvoltage').innerText = data.dc_bus_voltage.toFixed(2);
    // document.getElementById('uphasecurrent').innerText = data.U_phase_current.toFixed(2);
    // document.getElementById('power').innerText = data.power.toFixed(2);
    // // document.getElementById('dissipativeresistance').innerText = data.dissipativeresistance.toFixed(2);
    // // document.getElementById('daxieinductor').innerText = data.daxieinductor.toFixed(2);
    // // document.getElementById('qaxieinductor').innerText = data.qaxieinductor.toFixed(2);
    // // document.getElementById('reverseemfconstant').innerText = data.reverseemfconstant.toFixed(2);
    // // document.getElementById('polaritylog').innerText = data.polaritylog.toFixed(2);
    // document.getElementById('motorinputpower').innerText = data.motor_input_power.toFixed(2);
    // document.getElementById('torque').innerText = data.torque.toFixed(2);
    // document.getElementById('motoroutputpower').innerText = data.motor_output_power.toFixed(2);
    // document.getElementById('addload').innerText = data.load.toFixed(2);

    // document.getElementById('speedcompensationcoefficient').innerText = data.speed_loop_compensates_bandwidth.toFixed(2);
    // document.getElementById('currentbandwidth').innerText = data.current_loop_compensates_bandwidth.toFixed(2);
    // document.getElementById('observercompensationcoefficient').innerText = data.observer_compensates_bandwidth.toFixed(2);
    // document.getElementById('load').innerText = data.load.toFixed(2);
    // document.getElementById('speed').innerText = data.set_speed.toFixed(2);
    // if (data.breakdown != [])
    //     document.getElementById('faultinformation').innerText = "故障";
    // else document.getElementById('faultinformation').innerText = "良好";
});


window.addEventListener('beforeunload', function (e) {
    // 设置一个提示信息
    var confirmationMessage = '确定要离开此页吗？';
  
    if (auto_collect) {
    //   confirmationMessage = '数据采集正在进行中，确定要离开此页吗？可能会导致不可预期的后果';
      alert("数据采集正在进行，请先停止数据采集");
      return;
    } else {
        if (fan_running) {
            confirmationMessage = '风机正在运行，确定要离开此页吗？可能会导致不可预期的后果';
        }
        if (test_device_running) {
            confirmationMessage = '测试设备正在运行，确定要离开此页吗？可能会导致不可预期的后果';
        }
    }
    
    // 标准化事件对象
    e = e || window.event;
  
    // 对于IE和Firefox的早期版本
    if (e) {
      e.returnValue = confirmationMessage;
    }
  
    // 对于Chrome, Safari, Firefox 4+, Opera 12+
    return confirmationMessage;
  });
  