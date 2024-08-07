<script lang="ts" setup>
import { ref } from 'vue'
import { ElMessage } from 'element-plus'
import { useGlobalStore } from '@/stores/global'
import { useDBStore } from '@/stores/global'

const emit = defineEmits(['addFinished'])
const dialog = ref(false)
const loading = ref(false)

const global = useGlobalStore()
const db = useDBStore()
const formList = ref([])

const onClickAddButton = () => {
  try {
    dialog.value = true
    initFormList()
  } catch (error) {
    // console.log(error)
  }
}

const initFormList = () => {
  // console.log(db.columnsToFill)
  formList.value = []
  db.columnsToFill.forEach(item => {
    formList.value.push({
      key: item,
      value: null,
    })
  })
}

const handleAddDB = () => {
  loading.value = true
  let formToPOST = {}
  formList.value.forEach(element => {
    formToPOST[element.key] = element.value
    console.log(element.key)
  })

  fetch(global.url + '/db/data', {
    method: 'POST',
    body: JSON.stringify({ data_list: [formToPOST] }),
    headers: {
      'Content-Type': 'application/json'
    }
  })
    .then(response => response.json())
    .then(data => {
      emit('addFinished')
      loading.value = false
      dialog.value = false
      if (data.status == 'error') {
        throw new Error(data.message)
      }
      ElMessage({
        message: '数据添加成功',
        type: 'success'
      })
    })
    .catch(response => {
      ElMessage.error('数据添加失败:' + response.message)
    })
}

const cancelForm = () => {
  loading.value = false
  dialog.value = false
}

</script>

<template>
  <el-button style="margin: 0 10px 0 0;" type="primary" @click="onClickAddButton">添加</el-button>
  <el-drawer v-model="dialog" title="Add Database Item" direction="rtl" class="demo-drawer">
    <div class="addDBForm">
      <el-form :model="formList" label-width="auto">
        <el-form-item v-for="item in formList" :label="item.key">
          <el-input v-model="item.value" clearable />
        </el-form-item>
        <el-form-item>
          <el-button type="primary" @click="handleAddDB">ADD</el-button>
          <el-button type="primary" @click="cancelForm">Cancel</el-button>
        </el-form-item>
      </el-form>
    </div>
  </el-drawer>

</template>


<style>
.addDBForm {
  margin: auto;
}
</style>
