<script setup lang="ts">
import StatisticBox from '../components/StatisticBox.vue'
import ViewTitle from '../components/ViewTitle.vue'
import { io } from 'socket.io-client'
import { ref } from 'vue'
import { genFileId } from 'element-plus'
import { UploadInstance, UploadProps, UploadRawFile } from 'element-plus'

const contentDataShow = ref([])
const url = 'http://127.0.0.1:5000'
const urlCSV = url + '/collect/csvupload'
const socket = io(url)
const isConnected = ref(false)
const isFanRunning = ref(false)
const collectCount = ref(0)
const collectCountNow = ref(0)

const handleConnect = () => {
  if (isConnected.value == true) {
    socket.emit('disconnect_device')
  }
  else {
    socket.emit('connect_device')
  }
}

const upload = ref<UploadInstance>()

const handleExceed: UploadProps['onExceed'] = (files) => {
  upload.value!.clearFiles()
  const file = files[0] as UploadRawFile
  file.uid = genFileId()
  upload.value!.handleStart(file)
}

const submitUpload = () => {
  upload.value!.submit()
}

const uploadCSV = param => {
  const formData = new FormData()
  formData.append('file', param.file)
  fetch(urlCSV, {
    method: 'POST',
    body: formData,
  })
    .then(response => response.json())
    .then(data => {
      collectCount.value = data.line_count
    })
    .catch(response => {
      console.log('上传失败')
    })
}


const handleStartDevice = () => {
  var command = isFanRunning.value ? 'stop' : 'start'
  const formData = new FormData();
  formData.append('command', command);
  fetch(url + '/control/fan', {
    method: 'POST',
    body: formData,
  })
    .then(response => response.json())
    .then(data => {
      console.log('Server response:', data);
      if ('status' in data) {
        if (data.status == true) {
          isFanRunning.value = !isFanRunning.value
        } else {
          alert('设备启动失败');
        }
      }
    })
}


socket.on('connection', data => {
  if (data.status == true) {
    isConnected.value = true
  } else {
    isConnected.value = false
  }
})

socket.on('data_from_device', data => {
  delete data["breakdown"]
  contentDataShow.value = data
  console.log(data)
})

</script>

<template>
  <ViewTitle viewTitle="DashBoard" />
  <el-button type="primary" @click="handleConnect">{{ isConnected ? 'Disconnect' : 'Connect' }}</el-button>
  <el-button type="primary" @click="handleStartDevice" :disabled="!isConnected">
    {{ isFanRunning ? 'Stop Device' : 'Start Device' }}
  </el-button>

  <StatisticBox class="statisticBox" :contentObj="contentDataShow" title="" />
  <!-- <StatisticBox class="statisticBox" :contentObj="contentParaShow" title="ParaShow" /> -->

  <el-upload ref="upload" class="upload-demo" action="" :limit="1" :on-exceed="handleExceed" :auto-upload="false"
    :http-request="uploadCSV">
    <template #trigger>
      <el-button type="primary">select file</el-button>
    </template>
    <el-button class="ml-3" type="success" @click="submitUpload">
      upload to server
    </el-button>
  </el-upload>

  <el-text class="mx-1">共有{{ collectCount }}条数据需要采集，当前为第{{ collectCountNow }}条。</el-text>

</template>

<style scoped>
.statisticBox {
  margin: auto;
  min-height: 10vh;
}
</style>
