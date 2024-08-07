<script setup lang="ts">
import { ref } from 'vue'
import { UploadInstance, UploadProps, UploadRawFile, genFileId } from 'element-plus'
import { useGlobalStore, useDashboardStore } from '@/stores/global'

const upload = ref<UploadInstance>()
const global = useGlobalStore()
const dashboard = useDashboardStore()
const handleExceed: UploadProps['onExceed'] = (files) => {
  upload.value!.clearFiles()
  const file = files[0] as UploadRawFile
  file.uid = genFileId()
  upload.value!.handleStart(file)
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
      dashboard.collectCount = data.line_count
    })
    .catch(response => {
      console.log('上传失败')
    })
}

const submitUpload = () => {
  upload.value!.submit()
}

</script>

<template>
  <el-upload ref="upload" class="upload-demo" action="" :limit="1" :on-exceed="handleExceed" :auto-upload="false"
    :http-request="uploadCSV">
    <template #trigger>
      <el-button  type="primary">选择</el-button>
    </template>
    <el-button type="success" @click="submitUpload">上传</el-button>
    <el-button type="primary" @click="">开始</el-button>
    <el-button type="primary" @click="">暂停</el-button>
    <el-button type="primary" @click="">停止</el-button>
  </el-upload>
  <div>
    <el-text class="collectorCount" size="large" type="primary">
      共有{{ dashboard.collectCount }}条数据需要采集，当前为第{{ dashboard.collectCountNow }}条。
    </el-text>
  </div>

</template>

<style>
.collectorCount {
  margin: 15px 0;
}

.upload-demo .el-button {
  margin: 0 10px 0 0;
}
</style>