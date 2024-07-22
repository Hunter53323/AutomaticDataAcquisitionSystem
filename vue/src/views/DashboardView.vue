<script setup lang="ts">
import StatisticBox from '@/components/Dashboard/StatisticBox.vue'
import ViewTitle from '@/components/ViewTitle.vue'
import DataGraph from '@/components/Dashboard/DataGraph.vue'
import { io } from 'socket.io-client'
import { onMounted, ref } from 'vue'
import { UploadInstance, UploadProps, UploadRawFile, genFileId } from 'element-plus'
import { useGlobalStore } from '@/stores/global'
import { ElMessage } from 'element-plus'

const contentDataShow = ref([])
const global = useGlobalStore()
const socket = io(global.url)
const isConnected = ref(false)
const isFanRunning = ref(false)
const collectCount = ref(0)
const collectCountNow = ref(0)
// const dataMap = ref({})
const upload = ref<UploadInstance>()
const timeData = ref([])


const getCurrentTime = () => {
  //获取当前时间并打印
  let dt = new Date()
  // let yy = dt.getFullYear();
  // let mm = dt.getMonth() + 1;
  // let dd = dt.getDate();
  let hh = dt.getHours();
  let mf = dt.getMinutes() < 10 ? '0' + dt.getMinutes() : dt.getMinutes();
  let ss = dt.getSeconds() < 10 ? '0' + dt.getSeconds() : dt.getSeconds();
  let ms = dt.getMilliseconds() < 10 ? '0' + dt.getMilliseconds() : dt.getMilliseconds();
  // return yy + '/' + mm + '/' + dd + ' ' + hh + ':' + mf + ':' + ss;
  return hh + ':' + mf + ':' + ss + '.' + ms;
}


const handleConnect = () => {
  if (isConnected.value == true) {
    socket.emit('disconnect_device')
  }
  else {
    socket.emit('connect_device')
  }
}


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
  fetch(global.url + '/collect/csvupload', {
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
  fetch(global.url + '/control/fan', {
    method: 'POST',
    body: formData,
  })
    .then(response => response.json())
    .then(data => {
      if ('status' in data) {
        if (data.status == true) {
          isFanRunning.value = !isFanRunning.value
        } else {
          ElMessage.error('设备启动失败')
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

  timeData.value.push({
    time: getCurrentTime(),
    value: data['actual_speed']
  })
  console.log(timeData.value)
})


</script>

<template>
  <ViewTitle viewTitle="DashBoard" />

  <div class="controlBox">
    <el-button type="primary" @click="handleConnect">{{ isConnected ? 'Disconnect' : 'Connect'
      }}</el-button>
    <el-button type="primary" @click="handleStartDevice" :disabled="!isConnected">
      {{ isFanRunning ? 'Stop Device' : 'Start Device' }}
    </el-button>
  </div>

  <div class="statisticBox">
    <StatisticBox :contentObj="contentDataShow" title="" />
    <!-- <StatisticBox class="statisticBox" :contentObj="contentParaShow" title="ParaShow" /> -->
  </div>

  <div class="collectorBox">
    <el-divider />
    <el-upload ref="upload" class="upload-demo" action="" :limit="1" :on-exceed="handleExceed" :auto-upload="false"
      :http-request="uploadCSV">
      <template #trigger>
        <el-button type="primary">Select File</el-button>
      </template>
      <el-button type="success" @click="submitUpload">
        Upload
      </el-button>
    </el-upload>
    <el-text class="collectorCount">共有{{ collectCount }}条数据需要采集，当前为第{{ collectCountNow }}条。</el-text>
    <div class="collectorControl">
      <el-button type="success" @click="">开始</el-button>
      <el-button type="success" @click="">暂停</el-button>
      <el-button type="success" @click="">停止</el-button>
    </div>
  </div>

  <el-divider />
  <DataGraph :data="timeData" />

</template>



<style scoped>
.statisticBox {
  margin: auto;
  min-height: 10vh;
}

.collectorCount {
  margin: 10px 0;
}

.collectorControl {
  margin: 10px 0;
}

.divider {
  margin: 10px 0 10px 0;
}

.el-button {
  margin: 0 10px 0 0;
}
</style>
