<script setup lang="ts">
import { useGlobalStore, useDashboardStore } from '@/stores/global'
import DataShowSelection from '@/components/ShowSelection.vue'
import { ElMessage } from 'element-plus'
import { onMounted, ref } from 'vue';

const props = defineProps(['socket'])

const dashboard = useDashboardStore()
const global = useGlobalStore()
const modeSelect = ref('1')


const handleConnect = () => {
  var command = ""
  if (dashboard.isFanConnected) {
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
  formData.append('device_name', 'FanDriver');
  fetch(global.url + '/socketio_http/connect_device', {
    method: 'POST',
    body: formData,
  })
    .then(response => {
      if (response.ok) {
        return response.json();
      } else {
        ElMessage.error('被测设备连接失败');
        throw new Error('Network response was not ok ' + response.status);
      }
    })
    .then(() => {
      if (command == 'connect') {
        dashboard.isFanConnected = true;
      }
      if (command == 'disconnect') {
        dashboard.isFanConnected = false;
      }
    })
    .catch(error => {
    });
}


const handleStartDevice = () => {
  // TODO 时间数据清空需要等待后端接口返回 stable
  const command = dashboard.isFanRunning ? 'stop' : 'start'
  const formData = new FormData();
  formData.append('command', command);
  fetch(global.url + '/control/fan', {
    method: 'POST',
    body: formData,
  })
    .then(response => response.json())
    .then(data => {
      if ('status' in data) {
        if (data.status == true) {
          dashboard.isFanRunning = !dashboard.isFanRunning
        } else {
          ElMessage.error('被测设备启动失败')
        }
      }
    })
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
    <el-button-group>
      <el-button type="primary" @click="handleStartDevice" :disabled="!dashboard.isFanConnected" class="selectWraper">
        <el-select v-model="modeSelect" placeholder="选择" style="width: 80px" class="innerSelect"
          :disable="!dashboard.isFanConnected">
          <el-option label="P 模式" value="1" />
          <el-option label="N 模式" value="2" />
          <el-option label="N1 模式" value="3" />
        </el-select>
      </el-button>
      <el-button type="primary" :disabled="!dashboard.isFanConnected">
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