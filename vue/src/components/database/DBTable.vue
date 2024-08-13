<script lang="ts" setup>
import { reactive, ref, onMounted } from 'vue'
import { ElTable, ElMessage, ElMessageBox } from 'element-plus'
import AddDBButton from '@/components/database/AddDBButton.vue'
import DBPagination from '@/components/database/DBPagination.vue'
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
  // console.log(multipleSelection.value)
}


const dbDataUpdate = () => {
  fetch(global.url + "/db/data/pagev2?page=" + db.currentPage + "&per_page=" + db.pageSize, {
    method: 'GET',
  }).then(response => response.json())
    .then(data => {
      // console.log(data)
      dbDataObjList.value = data.data
      db.totalCount = data.total_count
    })
}

const handleDBDelete = () => {
  if (multipleSelection.value.length == 0) {
    ElMessage.error('请选择要删除的数据')
    return
  }
  ElMessageBox.confirm(
    '此行为将删除选中的数据！',
    'Warning',
    {
      confirmButtonText: 'OK',
      cancelButtonText: 'Cancel',
      type: 'warning',
    }
  )
    .then(() => {
      fetch(global.url + "/db/data", {
        method: 'DELETE',
        body: JSON.stringify({ ids_input: multipleSelection.value }),
        headers: {
          'Content-Type': 'application/json'
        }
      }).then(response => response.json())
        .then(data => {
          if (data.status == 'error') {
            throw new Error(data.message)
          }
          dbDataUpdate()
          ElMessage({
            message: '数据删除成功',
            type: 'success'
          })
        })
        .catch(response => {
          ElMessage.error('数据删除失败:' + response.message)
        })
    })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: '数据删除取消',
      })
    })
}
const handleDBClear = () => {
  ElMessageBox.confirm(
    '此行为将清除数据库中所有数据！',
    'Warning',
    {
      confirmButtonText: 'OK',
      cancelButtonText: 'Cancel',
      type: 'warning',
    }
  )
    .then(() => {
      fetch(global.url + "/db/data", {
        method: 'DELETE',
        body: JSON.stringify({ ids_input: [] }),
        headers: {
          'Content-Type': 'application/json'
        }
      }).then(response => response.json())
        .then(data => {
          if (data.status == 'error') {
            throw new Error(data.message)
          }
          dbDataUpdate()
          ElMessage({
            message: '数据清除成功',
            type: 'success'
          })
        })
        .catch(response => {
          ElMessage.error('数据清除失败:' + response.message)
        })
    })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: '数据清除取消',
      })
    })

}

const handleDBExport = () => {
  ElMessageBox.prompt('请输入导出数据文件名', {
    confirmButtonText: 'OK',
    cancelButtonText: 'Cancel',
    // inputPattern:
    //   /[\w!#$%&'*+/=?^_`{|}~-]+(?:\.[\w!#$%&'*+/=?^_`{|}~-]+)*@(?:[\w](?:[\w-]*[\w])?\.)+[\w](?:[\w-]*[\w])?/,
    inputErrorMessage: '非法文件名',
  })
    .then(({ value }) => {
      fetch(global.url + "/db/export?filename=" + value, {
        method: 'GET',
      }).then(response => response.json())
        .then(data => {
          if (data.status == 'error') {
            throw new Error(data.message)
          }
          alert(data.message)
          ElMessage({
            message: '数据导出成功',
            type: 'success'
          })
        })
        .catch(response => {
          ElMessage.error('数据导出失败:' + response.message)
        })
    })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: '数据导出取消',
      })
    })

}

const handlePageChange = () => {
  dbDataUpdate()
}

const handlePageSizeChange = () => {
  db.currentPage = 1
  dbDataUpdate()
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
  db.updateMeta()
  dbDataUpdate()
})

</script>


<template>

  <div class="operationButton">
    <AddDBButton @add-finished="dbDataUpdate()" />
    <el-button type="success" @click="handleDBExport">导出</el-button>
    <el-button type="danger" @click="handleDBDelete">删除</el-button>
    <el-button type="danger" @click="handleDBClear">清空</el-button>
  </div>
  <el-table :data="dbDataObjList" @selection-change="handleSelectionChange">
    <el-table-column type="selection" width="55" />
    <el-table-column v-for="key in db.colunmsShowSelected" :prop="key" :label="key" show-overflow-tooltip
      :width="key.length * 16 + 20">
      <template #header>
        <span>{{ key }}</span>
      </template>
    </el-table-column>
    <el-table-column fixed="right" label="操作" min-width="60">
      <template #default="scope">
        <el-button link type="danger" size="small" @click="handleDBEdit()">编辑</el-button>
        <!-- <el-button link type="danger" size="small" @click.prevent="handleDBDelete()" >删除</el-button> -->
      </template>
    </el-table-column>
  </el-table>
  <DBPagination @page-change="handlePageChange" @size-change="handlePageSizeChange" />
</template>

<style scoped>
.el-table {
  margin-top: 20px;
  width: 100%;
}

.operationButton .el-button {
  margin: 0 10px 0 0;
}
</style>
