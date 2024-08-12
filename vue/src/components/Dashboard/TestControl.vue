<script setup lang="ts">
import { useGlobalStore, useDashboardStore } from '@/stores/global'
import DataShowSelection from '@/components/ShowSelection.vue'
import { ElMessage } from 'element-plus'
import { onMounted } from 'vue';

const props = defineProps(['socket'])

const dashboard = useDashboardStore()
const global = useGlobalStore()


const handleConnect = () => {
  var command = ""
  if (dashboard.isTestConnected) {
    if (dashboard.isFanRunning || dashboard.isTestRunning || dashboard.isAutoCollecting) {
      ElMessage.error('请先停止风机、测试设备或自动采集');
      return;
    }
    command = 'disconnect';
  } else {
    command = 'connect';
  }
  const formData = new FormData();
  formData.append('command', command);
  formData.append('device_name', 'TestDevice');
  fetch(global.url + '/socketio_http/connect_device', {
    method: 'POST',
    body: formData,
  })
    .then(response => {
      if (response.ok) {
        return response.json();
      } else {
        ElMessage.error('测试设备连接失败');
        throw new Error('Network response was not ok ' + response.status);
      }
    })
    .then(() => {
      if (command == 'connect') {
        dashboard.isTestConnected = true;
        // document.getElementById('status').innerText = "已连接";
        // document.getElementById('status').style.color = "green";
        // document.getElementById('connect_button').innerText = '断开连接';
        // document.getElementById('start_device_button').disabled = false;
        // document.getElementById('start_test_device_button').disabled = false;
      }
      if (command == 'disconnect') {
        dashboard.isTestConnected = false;
        // document.getElementById('status').innerText = "未连接";
        // document.getElementById('status').style.color = "red";
        // document.getElementById('connect_button').innerText = '连接设备';
        // document.getElementById('start_device_button').disabled = true;
        // document.getElementById('start_test_device_button').disabled = true;
      }
    })
    .catch(error => {
      console.error('Error connecting device:', error);
    });
}


const handleStartDevice = () => {
  // TODO 时间数据清空需要等待后端接口返回 stable
  var command = dashboard.isTestRunning ? 'stop' : 'start'
  const formData = new FormData();
  formData.append('command', command);
  fetch(global.url + '/control/testdevice', {
    method: 'POST',
    body: formData,
  })
    .then(response => response.json())
    .then(data => {
      if ('status' in data) {
        if (data.status == true) {
          dashboard.isTestRunning = !dashboard.isTestRunning
        } else {
          ElMessage.error('测试设备启动失败')
        }
      }
    })
}


</script>

<template>

  <div class="controlBox">
    <el-button :type="dashboard.isTestConnected ? 'danger' : 'primary'" @click="handleConnect">
      {{ dashboard.isTestConnected ? '断连' : '连接' }}
    </el-button>
    <el-button :type="dashboard.isTestRunning ? 'danger' : 'primary'" @click="handleStartDevice"
      :disabled="!dashboard.isTestConnected">
      {{ dashboard.isTestRunning ? '停止' : '启动' }}
    </el-button>
    <el-button :type="dashboard.isTestRunning ? 'danger' : 'primary'" @click="handleStartDevice"
      :disabled="!dashboard.isTestConnected">
      清障
    </el-button>
  </div>


</template>

<style>
.controlBox .el-button {
  margin: 0 10px 0 0;
}
</style>