<script lang="ts" setup>
import { reactive, ref, onMounted } from 'vue'
import type { TableInstance } from 'element-plus'
import { ElTable, ElMessage } from 'element-plus'
import AddDBButton from '../components/AddDBButton.vue'
import { useGlobalStore } from '@/stores/global'

const global = useGlobalStore()
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
  fetch(global.url + "/db/data/pagev2", {
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

  <AddDBButton class="dbButton" :form="form" @add-finished="dbDataUpdate()" />
  <el-button class="dbButton" type="primary" @click="handleDBDelete(multipleSelection)">DELETE</el-button>
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

<style>
.dbButton {
  margin: 0 10px 0 10px;
}
</style>
