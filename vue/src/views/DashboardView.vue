<script setup lang="ts">
import StatisticBox from '@/components/StatisticBox.vue'
import ViewTitle from '@/components/ViewTitle.vue'
import { io } from 'socket.io-client'
import { onMounted, ref } from 'vue'
import { UploadInstance, UploadProps, UploadRawFile, genFileId } from 'element-plus'
import { Chart } from '@antv/g2'
import { useGlobalStore } from '@/stores/global'

const contentDataShow = ref([])
const global = useGlobalStore()
const socket = io(global.url)
const isConnected = ref(false)
const isFanRunning = ref(false)
const collectCount = ref(0)
const collectCountNow = ref(0)
const dataMap = ref({})


const data = [
  { genre: 'Sports', sold: 275 },
  { genre: 'Strategy', sold: 115 },
  { genre: 'Action', sold: 120 },
  { genre: 'Shooter', sold: 350 },
  { genre: 'Other', sold: 150 },
];


const renderChart = () => {
  const chart = new Chart({
    container: 'chart',
  })
  chart
    .interval()
    .data(data)
    .encode('x', 'genre')
    .encode('y', 'sold')
  chart.render()
}


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



// // 渲染可视化
// chart.render()


</script>

<template>
  <ViewTitle viewTitle="DashBoard" />
  <el-button type="primary" @click="handleConnect">{{ isConnected ? 'Disconnect' : 'Connect'
    }}</el-button>
  <el-button type="primary" @click="handleStartDevice" :disabled="!isConnected">
    {{ isFanRunning ? 'Stop Device' : 'Start Device' }}
  </el-button>

  <StatisticBox class="statisticBox" :contentObj="contentDataShow" :keyMap="dataMap" title="" />
  <!-- <StatisticBox class="statisticBox" :contentObj="contentParaShow" title="ParaShow" /> -->

  <el-divider />
  <el-upload ref="upload" class="upload-demo" action="" :limit="1" :on-exceed="handleExceed" :auto-upload="false"
    :http-request="uploadCSV">
    <template #trigger>
      <el-button type="primary">Select File</el-button>
    </template>
    <el-button class="ml-3" type="success" @click="submitUpload">
      Upload
    </el-button>
  </el-upload>

  <el-text class="collectorCount">共有{{ collectCount }}条数据需要采集，当前为第{{ collectCountNow }}条。</el-text>

  <div class="collectorControl">
    <el-button type="success" @click="submitUpload">开始</el-button>
    <el-button type="success" @click="submitUpload">暂停</el-button>
    <el-button type="success" @click="submitUpload">停止</el-button>
  </div>
  <el-divider />
  <el-button style="margin: 0 10px 0 0;" type="primary" @click="renderChart">Load</el-button>
  <div id="chart"></div>

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
