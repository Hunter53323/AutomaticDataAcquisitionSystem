var fan_running = false
var test_device_running = false
var auto_collect = false

function sendCSVToServer() {
    const fileInput = document.getElementById('csvFileInput');
    const file = fileInput.files[0];
  
    if (!file) {
      alert('请先选择一个文件');
      return;
    }
  
    const formData = new FormData();
    formData.append('file', file);
  
    fetch('/collect/csvupload', {
      method: 'POST',
      body: formData,
    })
    .then(response => response.json())
    .then(data => {
      console.log('Server response:', data);
      alert(data.message);
      if ('line_count' in data) {
        document.getElementById('data-count').innerText = data.line_count;
        document.getElementById('start_collect_button').disabled = false;
        fileInput.value = '';
      }
    })
    .catch(error => {
      console.error('Error uploading file:', error);
    });
}

function click_connect_button() {
    if (isConnected) {
      if (fan_running == true || test_device_running == true || auto_collect == true) {
        alert('请先停止风机、测试设备或自动采集');
        return;
      }
      socket.emit('disconnect_device');
    } else {
      socket.emit('connect_device');
    }
}

function start_device() {
  if (fan_running == false) {
    command = 'start';
  } else {
    command = 'stop';
  }
  const formData = new FormData();
  formData.append('command', command);
  fetch('/control/fan', {
      method: 'POST',
      body: formData,
  })
  .then(response => response.json())
  .then(data => {
    console.log('Server response:', data);
    if ('status' in data) {
      if (data.status == true){
        fan_running = !fan_running;
        if (fan_running == true) {
          document.getElementById('start_device_button').innerText = '停止风机';
        } else {
          document.getElementById('start_device_button').innerText = '启动风机';
        }
      } else {
        alert('设备启动失败');
      }
    }
  })
}

function start_test_device() {
  if (test_device_running == false) {
    command = 'start';
  } else {
    command = 'stop';
  }
  const formData = new FormData();
  formData.append('command', command);
  fetch('/control/testdevice', {
      method: 'POST',
      body: formData,
  })
  .then(response => response.json())
  .then(data => {
    console.log('Server response:', data);
    if ('status' in data) {
      if (data.status == true){
        test_device_running = !test_device_running;
        if (test_device_running == true) {
          document.getElementById('start_test_device_button').innerText = '停止测试设备';
        } else {
          document.getElementById('start_test_device_button').innerText = '启动测试设备';
        }
      } else {
        alert('设备启动失败');
      }
    }
  })
}

function click_start_collect_button() {
  if (isConnected == false) {
    alert('请先连接设备');
    return;
  }
    const formData = new FormData();
    formData.append('command', 'start');
    fetch('/collect/control', {
        method: 'POST',
        body: formData,
    })
    .then(response => response.json())
    .then(data => {
      console.log('Server response:', data);
        if (data.status == 'start'){
            document.getElementById('pause_collect_button').disabled = false;
            document.getElementById('stop_collect_button').disabled = false;
            document.getElementById('start_collect_button').disabled = true;
            auto_collect = true;
            setTimeout(current_progress, 1000); // 每秒轮询一次
        }
      }
    )
    .catch(error => {
      console.error('Signal error', error);
    });
}

function current_progress() {
    fetch('/collect/view', {
        method: 'GET',
    })
    .then(response => response.json())
    .then(data => {
      console.log('Server response:', data);
      document.getElementById('current-data-count').innerText = data.success
      if (data.complete == true && auto_collect == true) {
        click_stop_collect_button();
      } else {
        if (auto_collect != false) {
        setTimeout(current_progress, 1000); // 每秒轮询一次
      }}
      }
    )
    .catch(error => {
        console.error('Search error', error);
    });
}

function click_pause_collect_button() {
    const formData = new FormData();
    if (document.getElementById('pause_collect_button').innerText == '暂停') {
        formData.append('command', 'pause');
    } else {
        formData.append('command', 'continue');
    }
    fetch('/collect/control', {
        method: 'POST',
        body: formData,
      })
    .then(response => response.json())
    .then(data => {
      console.log('Server response:', data);
      if ('status' in data) {
        if (data.status == 'pause'){
            document.getElementById('pause_collect_button').innerText = '继续';
        }
        if (data.status == 'continue'){
            document.getElementById('pause_collect_button').innerText = '暂停';
        }
      }
    })
    .catch(error => {
      console.error('Command error', error);
    });
}

function click_stop_collect_button() {
    const formData = new FormData();
    formData.append('command', 'stop');
    fetch('/collect/control', {
        method: 'POST',
        body: formData,
      })
    .then(response => response.json())
    .then(data => {
      console.log('Server response:', data);
        if (data.status == 'stop'){
            alert('数据采集完成');
            document.getElementById('pause_collect_button').disabled = true;
            document.getElementById('start_collect_button').disabled = true;
            // document.getElementById('export_data').disabled = false;
            document.getElementById('pause_collect_button').innerText = '暂停';
            auto_collect = false;
            document.getElementById('stop_collect_button').disabled = true;
        }
      }
    )
    .catch(error => {
      console.error('Command error', error);
    });
}

function click_export_data_button() {
    // 导出目前的数据
}

function click_clear_button() {
    // 清空数据库，清空已经上传的文件
    if (auto_collect != false) {
        alert('请先停止自动采集');
        return;
    }
    if (confirm("确定要清空所有自动采集设置？")){
        // 确定
        document.getElementById('export_data').disabled = true;
        document.getElementById('pause_collect_button').disabled = true;
        document.getElementById('stop_collect_button').disabled = true;
        document.getElementById('start_collect_button').disabled = true;
        document.getElementById('data-count').innerText = 0;
        document.getElementById('current-data-count').innerText = 0;
        document.getElementById('pause_collect_button').innerText = '暂停';

        const formData = new FormData();
        formData.append('command', 'clear');
        fetch('/collect/control', {
            method: 'POST',
            body: formData,
          })
        .then(response => response.json())
        .then(data => {
          console.log('Server response:', data);
            if (data.status == 'clear'){
                alert('自动采集状态已清空，可以重新配置自动采集参数');
            }})
        .catch(error => {
          console.error('Command error', error);
        });
        }
    else {
        //取消
        return;
    }
    
}