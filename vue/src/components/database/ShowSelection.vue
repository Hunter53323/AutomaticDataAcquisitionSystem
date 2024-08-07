<script lang="ts" setup>
import { reactive, ref } from 'vue'
import { ElDrawer, ElMessageBox } from 'element-plus'
import { useDBStore } from '@/stores/global'

const db = useDBStore()

const dialog = ref(false)
const loading = ref(false)
const colunmsShowSelected = ref({})

const onClick = () => {
  db.colunmsShowSelected = db.columns.filter((item) => colunmsShowSelected.value.includes(item))
  loading.value = false
  dialog.value = false
}

const handleClose = () => {
  if (db.colunmsShowSelected == colunmsShowSelected.value) {
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
  colunmsShowSelected.value = ref(db.colunmsShowSelected)
}

const showSelect = () => {
  // console.log(db.colunmsShowSelected)
}

const openDialog = () => {
  dialog.value = true
  colunmsShowSelected.value = db.colunmsShowSelected
}

</script>

<template>
  <el-button style="margin: 0 10px 0 0;" type="primary" @click="openDialog">SETTINGS</el-button>
  <el-drawer v-model="dialog" title="选择你要显示的列" :before-close="handleClose" direction="rtl" class="demo-drawer">
    <el-checkbox-group v-model="colunmsShowSelected" @change="showSelect">
      <div style="margin: 10px 0 10px 25px;" v-for="col in db.columns">
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