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

const getWidth = (key) => {
  let baseLength = key.length
  db.dbDataObjList.forEach((element) => {
    baseLength = Math.max((element[key] != null ? element[key] : 0).toString().length, baseLength)
  })
  return baseLength * 16 + 20
}



dashboard.initList()
dashboard.updateDeviceState()
settings.updateProtocol()
settings.updateConf()
settings.updateDefined()
settings.updateUser()
settings.updateSteady()
db.updateMeta()
db.dbDataUpdate()

</script>


<template>

  <div class="operationButton">
    <el-button type="primary" @click="db.handleDBAdd">添加</el-button>
    <el-button type="success" @click="db.handleDBExport">导出</el-button>
    <el-button type="success" @click="db.handleStatementExport">报表</el-button>
    <el-button type="danger" @click="db.handleDBDelete(multipleSelection)">删除</el-button>
    <el-button type="danger" @click="db.handleDBClear">清空</el-button>
  </div>
  <el-table :data="db.dbDataObjList" @selection-change="handleSelectionChange" table-layout="auto">
    <el-table-column type="selection" width="55" fixed />
    <el-table-column v-for="key in db.colunmsShowSelected" :prop="key" :label="key" :width="getWidth(key)">
      <template #header>
        <span>{{ key }}</span>
      </template>
    </el-table-column>
    <el-table-column fixed="right" label="操作" width="120" header-align="center">
      <template #default="scope">
        <el-button link type="danger" size="small" @click="db.handleDBEdit(scope.row['ID'])">编辑</el-button>
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
