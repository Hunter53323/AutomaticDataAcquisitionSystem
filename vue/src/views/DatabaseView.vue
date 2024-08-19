<script lang="ts" setup>
import { reactive, ref, onMounted, h } from 'vue'
import { ElTable, ElButton } from 'element-plus'
import DBPagination from '@/components/database/DBPagination.vue'
import { useGlobalStore, useDashboardStore, useSettingsStore, useDBStore } from '@/stores/global'

const global = useGlobalStore()
const db = useDBStore()
const dashboard = useDashboardStore()
const settings = useSettingsStore()

const dbDataObjList = ref([])

const multipleSelection = ref([])

const handleSelectionChange = (val) => {
  multipleSelection.value = []
  val.forEach((element) => {
    multipleSelection.value.push(element.ID)
  })
}

const handleDBEdit = () => {
  const data = dbDataObjList.value.filter((element) => {
    return element.ID == multipleSelection.value[0]
  })[0]
  fetch(global.url + "/db/data", {
    method: 'PUT',
    body: JSON.stringify({
      ids_input: [], update_data: data
    }),
    headers: {
      'Content-Type': 'application/json'
    }
  })
}
dashboard.initList()
dashboard.initDeviceState()
settings.updateProtocol()
settings.updateConf()
settings.updateDefined()
settings.updateUser()
db.updateMeta()

</script>


<template>

  <div class="operationButton">
    <el-button type="primary" @click="db.handleDBAdd">添加</el-button>
    <el-button type="success" @click="db.handleDBExport">导出</el-button>
    <el-button type="success" @click="db.handleStatementExport">报表</el-button>
    <el-button type="danger" @click="db.handleDBDelete(multipleSelection)">删除</el-button>
    <el-button type="danger" @click="db.handleDBClear">清空</el-button>
  </div>
  <el-table :data="db.dbDataObjList" @selection-change="handleSelectionChange">
    <el-table-column type="selection" width="55" fixed />
    <el-table-column v-for="key in db.colunmsShowSelected" :prop="key" :label="key" show-overflow-tooltip
      :width="key.length * 16 + 20">
      <template #header>
        <span>{{ key }}</span>
      </template>
    </el-table-column>
    <el-table-column fixed="right" label="操作" width="120" header-align="center">
      <template #default="scope">
        <el-button link type="danger" size="small" @click="handleDBEdit">编辑</el-button>
        <el-button link type="danger" size="small" @click.prevent="db.handleDBDelete([scope.row['ID']])">删除</el-button>
      </template>
    </el-table-column>
  </el-table>
  <DBPagination />
</template>

<style>
.el-table {
  margin-top: 20px;
  width: 100%;
}

.operationButton .el-button {
  margin: 0 10px 0 0;
}
</style>
