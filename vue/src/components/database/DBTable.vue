<script lang="ts" setup>
import { reactive, ref, onMounted, h } from 'vue'
import { ElTable, ElMessage, ElMessageBox, ElForm, ElFormItem, ElInput } from 'element-plus'
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
    .catch(response => {
      ElMessage.error('无法获取数据，请检查数据库是否正常运行')
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
      customClass: "db-operation-box",
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
      customClass: "db-operation-box",
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
  const filename = ref('')
  const filepath = ref('')
  const conditions = ref('')
  ElMessageBox({
    title: '数据导出',
    message: h(ElForm,
      { labelWidth: "auto", labelPosition: "left" },
      () => [
        h(ElFormItem, { label: "导出文件名", required: true }, () => {
          return h(ElInput, { modelValue: filename.value, 'onUpdate:modelValue': val => filename.value = val }, null)
        }),
        h(ElFormItem, { label: "导出目录", required: true }, () => {
          return h(ElInput, { modelValue: filepath.value, "onUpdate:modelValue": val => filepath.value = val }, null)
        }),
        h(ElFormItem, { label: "筛选条件" }, () => {
          return h(ElInput, { modelValue: conditions.value, "onUpdate:modelValue": val => conditions.value = val }, null)
        }),
      ]),
    customClass: "db-operation-box",
    showCancelButton: true,
    confirmButtonText: '确认',
    cancelButtonText: '取消',
  })
    .then(() => {
      fetch(global.url + "/db/export?filename=" + filename + "?filepath=" + filepath, {
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

const handleStatementExport = () => {
  const filename = ref('')
  const filepath = ref('')
  const conditions = ref('')
  ElMessageBox({
    title: '报表导出',
    message: h(ElForm,
      { labelWidth: "auto", labelPosition: "left" },
      () => [
        h(ElFormItem, { label: "导出文件名", required: true }, () => {
          return h(ElInput, { modelValue: filename.value, 'onUpdate:modelValue': val => filename.value = val }, null)
        }),
        h(ElFormItem, { label: "导出目录", required: true }, () => {
          return h(ElInput, { modelValue: filepath.value, "onUpdate:modelValue": val => filepath.value = val }, null)
        }),
        h(ElFormItem, { label: "筛选条件" }, () => {
          return h(ElInput, { modelValue: conditions.value, "onUpdate:modelValue": val => conditions.value = val }, null)
        }),
      ]),
    customClass: "db-operation-box",
    showCancelButton: true,
    confirmButtonText: '确认',
    cancelButtonText: '取消',
  })
    .then(() => {
      fetch(global.url + "/db/statement?filename=" + filename + "?filepath=" + filepath, {
        method: 'GET',
      }).then(response => response.json())
        .then(data => {
          if (data.status == 'error') {
            throw new Error(data.message)
          }
          alert(data.message)
          ElMessage({
            message: '报表导出成功',
            type: 'success'
          })
        })
        .catch(response => {
          ElMessage.error('报表导出失败:' + response.message)
        })
    })
    .catch(() => {
      ElMessage({
        type: 'info',
        message: '报表导出取消',
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
    <el-button type="success" @click="handleStatementExport">报表</el-button>
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

<style>
.el-table {
  margin-top: 20px;
  width: 100%;
}

.operationButton .el-button {
  margin: 0 10px 0 0;
}

.db-operation-box .el-message-box__message {
  margin-top: 10px;
  width: 100%;
}

.db-operation-box .el-button {
  margin: 0 0 0 10px;
}
</style>
