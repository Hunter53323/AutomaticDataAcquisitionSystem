<script setup lang="ts">
import { useGlobalStore, useDashboardStore } from '@/stores/global'
import DataShowSelection from '@/components/Dashboard/DataShowSelection.vue'
import { ElMessage } from 'element-plus'

const props = defineProps(['socket'])

const dashboard = useDashboardStore()
const global = useGlobalStore()


const handleConnect = () => {
  if (dashboard.isConnected == true) {
    props.socket.emit('disconnect_device')
  }
  else {
    props.socket.emit('connect_device')
  }
}


const handleStartDevice = () => {
  // TODO 时间数据清空需要等待后端接口返回 stable
  var command = dashboard.isFanRunning ? 'stop' : 'start'
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
          ElMessage.error('设备启动失败')
        }
      }
    })
}

</script>

<template>

  <div class="controlBox">
    <el-button type="primary" @click="handleConnect">
      {{ dashboard.isConnected ? '断连' : '连接' }}
    </el-button>
    <el-button type="primary" @click="handleStartDevice" :disabled="!dashboard.isConnected">
      {{ dashboard.isFanRunning ? '停止' : '启动' }}
    </el-button>
  </div>


</template>

<style>
.controlBox .el-button {
  margin: 0 10px 0 0;
}
</style>