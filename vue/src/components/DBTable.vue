<script lang="ts" setup>
import { reactive, ref, onMounted } from 'vue'
import type { TableInstance } from 'element-plus'
import { ElTable, ElMessage } from 'element-plus'
import AddDBButton from '../components/AddDBButton.vue'
import { useGlobalStore } from '@/stores/global'
import { useDBStore } from '@/stores/global'

const global = useGlobalStore()
const db = useDBStore()
const dbDataObjList = ref([])

const multipleSelection = ref([])

const handleSelectionChange = (val) => {
  multipleSelection.value = []
  val.forEach((element) => {
    multipleSelection.value.push(element.ID)
  })
  console.log(multipleSelection.value)
}


const dbDataUpdate = () => {
  fetch(global.url + "/db/data/pagev2", {
    method: 'GET',
  }).then(response => response.json())
    .then(data => {
      console.log(data)
      dbDataObjList.value = data.data
    })
}


const tableLayout = ref<TableInstance['tableLayout']>('auto')

const handleDBDelete = (id) => {
  if (id == false) {
    return
  }
  fetch(global.url + "/db/data", {
    method: 'DELETE',
    body: JSON.stringify({ ids_input: id }),
    headers: {
      'Content-Type': 'application/json'
    }
  }).then(response => response.json())
    .then(data => {
      dbDataUpdate()
      ElMessage({
        message: '数据删除成功',
        type: 'success'
      })
    })
    .catch(response => {
      ElMessage.error('数据删除失败')
    })
}
const handleDBClear= ()=>{
  fetch(global.url + "/db/data", {
    method: 'DELETE',
    body: JSON.stringify({ ids_input: [] }),
    headers: {
      'Content-Type': 'application/json'
    }
  }).then(response => response.json())
    .then(data => {
      dbDataUpdate()
      ElMessage({
        message: '数据清除成功',
        type: 'success'
      })
    })
    .catch(response => {
      ElMessage.error('数据清除失败')
    })
}



const handleDBEdit = () => {
  fetch(global.url + "/db/data", {
    method: 'PUT',
    body: JSON.stringify({ ids_input: [] }),
    headers: {
      'Content-Type': 'application/json'
    }
  })
}

onMounted(() => {
  dbDataUpdate()
})

</script>


<template>

  <AddDBButton @add-finished="dbDataUpdate()" />
  <el-button style="margin: 0 10px 0 10px;" type="primary" @click="handleDBDelete(multipleSelection)">DELETE</el-button>
  <el-button style="margin: 0 10px 0 10px;" type="primary" @click="handleDBClear()">CLEAR</el-button>
  <el-table :data="dbDataObjList" style="width: 100%" :table-layout="tableLayout"
    @selection-change="handleSelectionChange">
    <el-table-column type="selection" width="55" />
    <el-table-column v-for="key in db.columns" :prop="key" :label="key" />
    <el-table-column fixed="right" label="Operations" min-width="120">
      <template #default="scope">
        <el-button link type="primary" size="small" @click="handleDBEdit()">Edit</el-button>
        <el-button link type="primary" size="small"
          @click.prevent="handleDBDelete([dbDataObjList[scope.$index].ID])">Delete</el-button>
      </template>
    </el-table-column>
  </el-table>

</template>
