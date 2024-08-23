<script setup lang="ts">
import { useGlobalStore, useDashboardStore } from '@/stores/global'
import DataShowSelection from '@/components/ShowSelection.vue'
import { ElMessage } from 'element-plus'
import { onMounted, ref } from 'vue';

const props = defineProps(['socket'])

const dashboard = useDashboardStore()
const global = useGlobalStore()


const handleConnect = () => {
  var command = ""
  if (dashboard.isFanConnected) {
    if (dashboard.isFanRunning || dashboard.isTestRunning || dashboard.autoCollectStatus == 3 || dashboard.autoCollectStatus == 4) {
      ElMessage.error('请先停止风机、测试设备或自动采集');
      return;
    }
    command = 'disconnect';
  } else {
    command = 'connect';
  }
  const formData = new FormData();
  formData.append('command', command);
  formData.append('device_name', 'FanDriver');
  fetch(global.url + '/socketio_http/connect_device', {
    method: 'POST',
    body: formData,
  })
    .then(response => {
      if (response.ok) {
        ElMessage.success('被测设备' + (command == 'disconnect' ? '断连' : '连接') + '成功');
        return response.json();

      } else {
        throw new Error('Network response was not ok ' + response.status);
      }
    })
    .then(() => {
    })
    .catch(error => {
      ElMessage.error('被测设备' + (command == 'disconnect' ? '断连' : '连接') + '失败');
      dashboard.updateDeviceState()
    });
}


const handleStartDevice = () => {
  const command = dashboard.isFanRunning ? 'stop' : 'start'
  const formData = new FormData();
  formData.append('command', command);
  fetch(global.url + '/control/fan', {
    method: 'POST',
    body: formData,
  })
    .then(response => response.json())
    .then(data => {
      if (data.status == true) {
        dashboard.isFanRunning = !dashboard.isFanRunning
        ElMessage.success('被测设备' + (command == 'stop' ? '停止' : '启动') + '成功')
      }
      else {
        throw new Error();
      }
    })
    .catch(error => {
      ElMessage.error('被测设备' + (command == 'stop' ? '停止' : '启动') + '失败')
      dashboard.updateDeviceState()
    });
}

const handleClearBreakdown = () => {
  const command = 'clear_breakdown'
  const formData = new FormData();
  formData.append('command', command);
  fetch(global.url + '/control/fan', {
    method: 'POST',
    body: formData,
  })
    .then(response => response.json())
    .then(data => {
      if (data.status == true) {
        dashboard.isFanRunning = !dashboard.isFanRunning
        ElMessage.success('被测设备清障成功')
      }
      else {
        throw new Error();
      }
    })
    .catch(error => {
      ElMessage.error('被测设备清障失败')
      dashboard.updateDeviceState()
    });
}

</script>

<template>

  <div class="controlBox">
    <el-button :type="dashboard.isFanConnected ? 'danger' : 'primary'" @click="handleConnect">
      {{ dashboard.isFanConnected ? '断连' : '连接' }}
    </el-button>
    <el-button :type="dashboard.isFanRunning ? 'danger' : 'primary'" @click="handleStartDevice"
      :disabled="!dashboard.isFanConnected">
      {{ dashboard.isFanRunning ? '停止' : '启动' }}
    </el-button>
    <el-button :type="dashboard.isTestRunning ? 'danger' : 'primary'" @click="handleClearBreakdown"
      :disabled="(!dashboard.isFanConnected || !dashboard.isFanBreakDown)">
      清障
    </el-button>

  </div>


</template>

<style>
.controlBox .el-button {
  margin: 0 10px 0 0;
}
</style>