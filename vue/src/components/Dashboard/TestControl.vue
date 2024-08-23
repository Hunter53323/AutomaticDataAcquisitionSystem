<script setup lang="ts">
import { useGlobalStore, useDashboardStore } from '@/stores/global'
import DataShowSelection from '@/components/ShowSelection.vue'
import { ElMessage } from 'element-plus'
import { ref } from 'vue';

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
        ElMessage.success('测试设备' + (command == 'disconnect' ? '断连' : '连接') + '成功');
        return response.json();
      } else {
        throw new Error();
      }
    })
    .then(() => {
      if (command == 'connect') {
        dashboard.isTestConnected = true;
      }
      if (command == 'disconnect') {
        dashboard.isTestConnected = false;
      }
      dashboard.updateDeviceState()
    })
    .catch(error => {
      ElMessage.error('测试设备' + (command == 'disconnect' ? '断连' : '连接') + '失败');
      dashboard.updateDeviceState()
    });
}


const handleStartDevice = () => {
  var command = dashboard.isTestRunning ? 'stop' : 'start'
  const formData = new FormData();
  formData.append('command', command);
  fetch(global.url + '/control/testdevice', {
    method: 'POST',
    body: formData,
  })
    .then(response => response.json())
    .then(data => {
      if (data.status == true) {
        ElMessage.success('测试设备' + (command == 'stop' ? '停止' : '启动') + '成功')
        dashboard.isTestRunning = !dashboard.isTestRunning
      } else {
        throw new Error();
      }
      dashboard.updateDeviceState()
    })
    .catch(error => {
      ElMessage.error('测试设备' + (command == 'stop' ? '停止' : '启动') + '失败')
      dashboard.updateDeviceState()
    });
}

const modeSelect = ref('1')


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
    <el-button-group>
      <el-button type="primary" @click="handleStartDevice" :disabled="!dashboard.isTestConnected" class="selectWraper">
        <el-select v-model="modeSelect" placeholder="选择" style="width: 80px" class="innerSelect"
          :disable="!dashboard.isFanConnected">
          <el-option label="P 模式" value="1" />
          <el-option label="N 模式" value="2" />
          <el-option label="N1 模式" value="3" />
        </el-select>
      </el-button>
      <el-button type="primary" :disabled="!dashboard.isTestConnected">
        设置
      </el-button>
    </el-button-group>

  </div>


</template>

<style>
.controlBox .el-button {
  margin: 0 10px 0 0;
}

.innerSelect .el-select__wrapper {
  box-shadow: none;
  background: none;
  width: 120px;
}

.innerSelect .el-select__selected-item {
  color: #fff;
}

.innerSelect .el-select__icon {
  color: #fff;
}

.selectWraper {
  padding: 0;
  margin: 0;
  width: 120px;
  display: flex;
  justify-content: space-between;
}
</style>