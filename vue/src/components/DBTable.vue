<script lang="ts" setup>
import { reactive, ref, onMounted } from 'vue'
import type { TableInstance } from 'element-plus'
import { ElTable } from 'element-plus'
import AddDBButton from '../components/AddDBButton.vue'
import DeleteDBButton from '../components/DeleteDBButton.vue'

const url = 'http://127.0.0.1:5000'
const dbDataObjList = ref([])

const multipleSelection = ref([])

const form = reactive({
  '风机名称': 0,
  '风机型号': 0,
  '转速': 0,
  '速度环补偿系数': 0,
  '电流环带宽': 0,
  '观测器补偿系数': 0,
  '负载量': 0,
  '功率': 0
})
const dbKeysList = ['ID', ...Object.keys(form), '时间戳']

const handleSelectionChange = (val) => {
  multipleSelection.value = []
  val.forEach((element) => {
    multipleSelection.value.push(element.ID)
  })
  console.log(multipleSelection.value)
}

const dbDataUpdate = () => {
  dbDataObjList.value = []
  fetch(url + "/db/data/page", {
    method: 'GET',
  }).then(response => response.json())
    .then(data => {
      const dbDataRawList = data.data
      dbDataRawList.forEach((item) => {
        const tmpDBDataObj = {}
        item.forEach((element, index) => {
          tmpDBDataObj[dbKeysList[index]] = element
        })
        dbDataObjList.value.push(tmpDBDataObj)
      })
    })
}
const tableLayout = ref<TableInstance['tableLayout']>('auto')

const handleDBDelete = (id) => {
  fetch(url + "/db/data", {
    method: 'DELETE',
    body: JSON.stringify({ ids_input: id }),
    headers: {
      'Content-Type': 'application/json'
    }
  }).then(response => response.json())
    .then(data => {
      dbDataUpdate()
    })
}

const handleDBEdit = () => {
  fetch(url + "/db/data", {
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

  <AddDBButton :form="form" />
  <DeleteDBButton :selectList="multipleSelection" />
  <el-table :data="dbDataObjList" style="width: 100%" :table-layout="tableLayout"
    @selection-change="handleSelectionChange">
    <el-table-column type="selection" width="55" />
    <el-table-column v-for="key in dbKeysList" :prop="key" :label="key" />
    <el-table-column fixed="right" label="Operations" min-width="120">
      <template #default="scope">
        <el-button link type="primary" size="small" @click="handleDBEdit()">Edit</el-button>
        <el-button link type="primary" size="small"
          @click.prevent="handleDBDelete([dbDataObjList[scope.$index].ID])">Delete</el-button>
      </template>
    </el-table-column>
  </el-table>

</template>
