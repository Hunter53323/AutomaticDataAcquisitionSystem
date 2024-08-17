<script setup lang="ts">
import { ref } from 'vue'
import { ElMessage, UploadInstance, UploadProps, UploadRawFile, genFileId } from 'element-plus'
import { useGlobalStore, useDashboardStore } from '@/stores/global'

const upload = ref<UploadInstance>()
const global = useGlobalStore()
const dashboard = useDashboardStore()
const uploadDisable = ref(false)
const startDisable = ref(true)
const stopDisable = ref(true)
const pauseDisable = ref(true)
const clearDisable = ref(true)
const continueDisable = ref(true)


const handleExceed: UploadProps['onExceed'] = (files) => {
  upload.value!.clearFiles()
  const file = files[0] as UploadRawFile
  file.uid = genFileId()
  upload.value!.handleStart(file)
}

const uploadCSV = (param) => {
  const formData = new FormData()
  formData.append('file', param.file)
  fetch(global.url + '/collect/csvupload', {
    method: 'POST',
    body: formData,
  })
    .then(response => response.json())
    .then(data => {
      if (data.message != "文件上传成功") {
        throw new Error(data.message)
      }
      ElMessage.success('数采配置文件上传成功')
      dashboard.collectCount = data.line_count
      dashboard.updateCollectState()
      startDisable.value = false
    })
    .catch(err => {
      ElMessage.error('数采配置文件上传失败' + err)
    })
}

const submitUpload = () => {
  upload.value!.submit()
}

const collectorStart = () => {
  const formData = new FormData();
  formData.append('command', 'start');
  fetch(global.url + '/collect/control', {
    method: 'POST',
    body: formData
  })
    .then(response => response.json())
    .then(data => {
      if (data.status == 'error') {
        throw new Error(data.message)
      }
      ElMessage.success('数采开始成功')
      startDisable.value = true
      stopDisable.value = false
      pauseDisable.value = false
      clearDisable.value = false
      continueDisable.value = true
      uploadDisable.value = true
    })
    .catch(response => {
      ElMessage.error('数采开始失败')
    })
}

const collectorPause = () => {
  const formData = new FormData();
  formData.append('command', 'pause');
  fetch(global.url + '/collect/control', {
    method: 'POST',
    body: formData
  })
    .then(response => response.json())
    .then(data => {
      if (data.status == 'error') {
        throw new Error()
      }
      ElMessage.success('数采暂停成功')
      startDisable.value = false
      stopDisable.value = false
      pauseDisable.value = true
      clearDisable.value = false
      continueDisable.value = false
      uploadDisable.value = true
    })
    .catch(response => {
      ElMessage.error('数采暂停失败')
    })
}

const collectorStop = () => {
  const formData = new FormData();
  formData.append('command', 'stop');
  fetch(global.url + '/collect/control', {
    method: 'POST',
    body: formData
  })
    .then(response => response.json())
    .then(data => {
      if (data.status == 'error') {
        throw new Error()
      }
      ElMessage.success('数采停止成功')
      startDisable.value = true
      stopDisable.value = true
      pauseDisable.value = true
      clearDisable.value = false
      continueDisable.value = false
      uploadDisable.value = true
    })
    .catch(response => {
      ElMessage.error('数采停止失败')
    })
}

const collectorContinue = () => {
  const formData = new FormData();
  formData.append('command', 'continue');
  fetch(global.url + '/collect/control', {
    method: 'POST',
    body: formData
  })
    .then(response => response.json())
    .then(data => {
      if (data.status == 'error') {
        throw new Error()
      }
      ElMessage.success('数采继续成功')
      startDisable.value = true
      stopDisable.value = false
      pauseDisable.value = false
      clearDisable.value = false
      continueDisable.value = true
      uploadDisable.value = true
    })
    .catch(response => {
      ElMessage.error('数采继续失败')
    })
}

const collectorClear = () => {
  const formData = new FormData();
  formData.append('command', 'clear');
  fetch(global.url + '/collect/control', {
    method: 'POST',
    body: formData
  })
    .then(response => response.json())
    .then(data => {
      if (data.status == 'error') {
        throw new Error()
      }
      ElMessage.success('数采清空成功')
      startDisable.value = false
      stopDisable.value = true
      pauseDisable.value = true
      clearDisable.value = true
      continueDisable.value = false
      uploadDisable.value = true
    })
    .catch(response => {
      ElMessage.error('数采清空失败')
    })
}

</script>

<template>
  <el-upload ref="upload" class="upload-demo" :limit="1" :on-exceed="handleExceed" :auto-upload="false"
    :http-request="uploadCSV">
    <template #trigger>
      <el-button type="primary" :disabled="uploadDisable">选择</el-button>
    </template>
    <el-button type="success" @click="submitUpload">上传</el-button>
    <el-button type="primary" @click="collectorStart" :disabled="startDisable">开始</el-button>
    <el-button type="primary" @click="collectorPause" :disabled="pauseDisable">暂停</el-button>
    <el-button type="primary" @click="collectorStop" :disabled="stopDisable">停止</el-button>
    <el-button type="primary" @click="collectorContinue" :disabled="continueDisable">继续</el-button>
    <el-button type="primary" @click="collectorClear" :disabled="clearDisable">清空</el-button>
  </el-upload>
  <div>
    <el-text class="collectorCount" size="large" type="primary">
      共{{ dashboard.collectCount }}条，剩余{{ dashboard.remainCount }}条，成功{{ dashboard.successCount }}条，
      失败{{ dashboard.failCount }}条
    </el-text>
  </div>

</template>

<style scoped>
.collectorCount {
  margin: 15px 0;
}

.upload-demo .el-button {
  margin: 0 10px 0 0;
}
</style>