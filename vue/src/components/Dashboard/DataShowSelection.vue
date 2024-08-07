<script setup>
import { reactive, ref } from 'vue'
import { ElDrawer, ElMessageBox } from 'element-plus'
import { useDashboardStore } from '@/stores/global'

const dashboard = useDashboardStore()

const dialog = ref(false)
const loading = ref(false)
const dataShowSelected = ref([])

const onClick = () => {
  dashboard.dataShowSelected = dataShowSelected.value
  loading.value = false
  dialog.value = false
}

const handleClose = () => {
  if (dashboard.dataShowSelected == dataShowSelected.value) {
    dialog.value = false
    return 
  }
  ElMessageBox.confirm('配置更改未保存，确认关闭？')
    .then(() => {
      loading.value = false
      dialog.value = false
    })
    .catch(() => {
      // catch error
    })
}

const cancelForm = () => {
  loading.value = false
  dialog.value = false
  dataShowSelected.value = ref(dashboard.colunmsShowSelected)
}

const showSelect = () => {
  console.log(dashboard.colunmsShowSelected)
}

const openDialog = () => {
  dialog.value = true
  dataShowSelected.value = dashboard.colunmsShowSelected
}


</script>

<template>
  <el-button style="margin: 0 10px 0 0;" type="primary" @click="openDialog">SETTINGS</el-button>
  <el-drawer v-model="dialog" title="选择你要显示的数据" :before-close="handleClose" direction="rtl" class="demo-drawer">
    <el-checkbox-group v-model="dataShowSelected" @change="showSelect">
      <div style="margin: 10px 0 10px 25px;" v-for="col in dashboard.dataList">
        <el-checkbox :key="col" :label="col" :value="col">
          {{ col }}
        </el-checkbox>
      </div>
    </el-checkbox-group>
    <div style="margin: 20px 0 0 0;">
      <el-button style="margin: 0 10px 0 0;" type="primary" @click="onClick" :loading="loading">Submit</el-button>
      <el-button style="margin: 0 10px 0 0;" @click="cancelForm">Cancel</el-button>
    </div>
  </el-drawer>
</template>