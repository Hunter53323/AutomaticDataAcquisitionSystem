<script lang="ts" setup>
import { reactive, ref, onMounted } from 'vue'
import type { TableInstance } from 'element-plus'
import { ElTable, ElMessage, ElMessageBox } from 'element-plus'
import AddDBButton from '../components/AddDBButton.vue'
import DBPagination from '../components/DBPagination.vue'
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
  fetch(global.url + "/db/data/pagev2?page=" + db.currentPage + "&per_page=" + db.pageSize, {
    method: 'GET',
  }).then(response => response.json())
    .then(data => {
      // console.log(data)
      dbDataObjList.value = data.data
      db.updateTotalCount(data.total_count)
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
          ElMessage.error('数据删除失败' + response.message)
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
          ElMessage.error('数据清除失败' + response.message)
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
          ElMessage.error('数据导出失败' + response.message)
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
  db.changeCurrentPage(1)
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
  dbDataUpdate()
})

</script>


<template>

  <AddDBButton @add-finished="dbDataUpdate()" />
  <el-button style="margin: 0 10px 0 0;" type="primary" @click="handleDBDelete">DELETE</el-button>
  <el-button style="margin: 0 10px 0 0;" type="primary" @click="handleDBClear">CLEAR</el-button>
  <el-button style="margin: 0 10px 0 0;" type="primary" @click="handleDBExport">EXPORT</el-button>
  <el-table :data="dbDataObjList" table-layout="auto" @selection-change="handleSelectionChange">
    <el-table-column type="selection" width="55" />
    <el-table-column v-for="key in db.columns" :prop="key" :label="key" />
    <el-table-column fixed="right" label="Operations" min-width="120">
      <template #default="scope">
        <el-button link type="primary" size="small" @click="handleDBEdit()">Edit</el-button>
        <el-button link type="primary" size="small" @click.prevent="handleDBDelete()">Delete</el-button>
      </template>
    </el-table-column>
  </el-table>
  <DBPagination @page-change="handlePageChange" @size-change="handlePageSizeChange" />
</template>

<style>
.el-table {
  margin-top: 20px;
  width: 100%;
}
</style>
