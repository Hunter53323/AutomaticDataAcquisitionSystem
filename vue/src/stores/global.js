import { defineStore } from 'pinia'
import { ref, h, reactive } from 'vue'
import { ElMessage, ElMessageBox, ElForm, ElFormItem, ElInput } from 'element-plus'
import DBExportBox from '@/components/database/DBExportBox.vue'
import StatementBox from '@/components/database/StatementBox.vue'
import DBAddBox from '@/components/database/DBAddBox.vue'

export const useGlobalStore = defineStore('global', {
  state: () => {
    return {
      url: 'http://127.0.0.1:5000'
    }
  }
})

export const useDBStore = defineStore('database', {
  state: () => ({
    columns: [],
    columnsToFill: [],
    colunmsShowSelected: [],
    dbDataObjList: [],
    totalCount: 0,
    pageSize: 10,
    currentPage: 1
  }),
  actions: {
    updateMeta() {
      fetch(useGlobalStore().url + "/db/data/meta", {
        method: 'GET'
      })
        .then(response => response.json())
        .then(data => {
          if ([...this.columns].join() != data.columns.join()) {
            this.columns = data.columns
            this.columnsToFill = data.columns_to_fill
            this.colunmsShowSelected = data.columns
          }
          this.totalCount = data.total_count
        })
    },
    dbDataUpdate() {
      fetch(useGlobalStore().url + "/db/data/pagev2?page=" + this.currentPage + "&per_page=" + this.pageSize, {
        method: 'GET',
      }).then(response => response.json())
        .then(data => {
          this.totalCount = data.total_count
          this.dbDataObjList = data.data
        })
        .catch(response => {
          ElMessage.error('无法获取数据，请检查数据库是否正常运行')
        })
    },
    handleDBDelete(ids) {
      console.log(ids)
      if (ids.length == 0) {
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
          fetch(useGlobalStore().url + "/db/data", {
            method: 'DELETE',
            body: JSON.stringify({ ids_input: ids }),
            headers: {
              'Content-Type': 'application/json'
            }
          }).then(response => response.json())
            .then(data => {
              if (data.status == 'error') {
                throw new Error(data.message)
              }
              this.dbDataUpdate()
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
    },
    handleDBClear() {
      ElMessageBox.confirm(
        '此行为将清除数据库中所有数据！',
        'Warning',
        {
          customClass: "db-operation-box",
          confirmButtonText: '确认',
          cancelButtonText: '取消',
          type: 'warning',
        }
      )
        .then(() => {
          fetch(useGlobalStore().url + "/db/data", {
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
              this.dbDataUpdate()
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

    },
    handleDBExport() {
      const form = reactive({
        filepath: '',
        filename: '',
        conditions: ''
      })
      ElMessageBox({
        title: '数据导出',
        message: h(DBExportBox, { modelValue: form, 'onUpdate:modelValue': value => form = value }),
        customClass: "db-operation-box",
        showCancelButton: true,
        confirmButtonText: '确认',
        cancelButtonText: '取消',
      })
        .then(() => {
          fetch(useGlobalStore().url + "/db/export?filename=" + form.filename + "?filepath=" + form.filepath, {
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
        .catch((e) => {
          ElMessage({
            type: 'info',
            message: '数据导出取消',
          })
          console.log(e)
        })

    },
    handleStatementExport() {
      const form = reactive({
        filepath: '',
        filename: '',
        conditions: ''
      })
      ElMessageBox({
        title: '报表导出',
        message: h(StatementBox, { modelValue: form, 'onUpdate:modelValue': value => form = value }),
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

    },
    handleDBAdd() {
      const form = reactive({})
      this.columnsToFill.forEach((column) => {
        form[column] = ''
      })
      ElMessageBox({
        title: '添加数据',
        message: h(DBAddBox, { modelValue: form, 'onUpdate:modelValue': value => form = value }),
        showCancelButton: true,
        customClass: "db-operation-box",
        confirmButtonText: '确认',
        cancelButtonText: '取消',
      }).then(() => {
        fetch(useGlobalStore().url + "/db/data", {
          method: 'POST',
          body: JSON.stringify(form),
          headers: {
            'Content-Type': 'application/json'
          }
        }).then(response => response.json())
          .then(data => {
            console.log(data)
            if (data.status == 'error') {
              throw new Error(data.message)
            }
            this.dbDataUpdate()
            ElMessage({
              message: '数据添加成功',
              type: 'success'
            })
          })
          .catch(response => {
            ElMessage.error('数据添加失败:' + response.message)
          })
      })
        .catch(() => {
          ElMessage({
            type: 'info',
            message: '数据添加取消',
          })
        })
    },
  }
})

export const useDashboardStore = defineStore('dashboard', {
  state: () => ({
    collectCount: 0,
    collectCountNow: 0,
    isFanConnected: false,
    isTestConnected: false,
    isFanRunning: false,
    isTestRunning: false,
    isFanBreakDown: false,
    isTestBreakDown: false,
    isAutoCollecting: false,
    dataList: {},
    dataShowSelected: {},
    paraList: [],
    paraShowSelected: [],

  }),
  actions: {
    initList() {
      fetch(useGlobalStore().url + "/control/data", {
        method: 'GET'
      })
        .then(response => response.json())
        .then(data => {
          // console.log(data)
          this.dataList = Object.assign({}, data)
          this.dataShowSelected = Object.assign({}, this.dataList)
        })
        .catch(error => {
          ElMessage({
            message: '无法获取数据名，请检查服务器是否正常运行！',
            type: 'error'
          })
        })
      fetch(useGlobalStore().url + "/control/parameters", {
        method: 'GET'
      })
        .then(response => response.json())
        .then(data => {
          this.paraList = [...data['FanDriver'], ...data['TestDevice']]
          this.paraShowSelected = this.paraList.slice(0)
        })
        .catch(error => {
          ElMessage({
            message: '无法获取参数名，请检查服务器是否正常运行！',
            type: 'error'
          })
        })
    },
    initDeviceState() {
      fetch(useGlobalStore().url + '/control/state', {
        method: 'GET',
      })
        .then((response) => response.json())
        .then((data) => {
          this.isFanConnected = data.FanDriver.connected
          this.isFanRunning = data.FanDriver.running
          this.isFanBreakDown = data.FanDriver.breakdown
          this.isTestConnected = data.TestDevice.connected
          this.isTestRunning = data.TestDevice.running
          this.isTestBreakDown = data.TestDevice.breakdown
        })
        .catch(error => {
          ElMessage({
            message: '无法获取设备状态，请检查服务器是否正常运行！',
            type: 'error'
          })
        })
    }
  }
})
export const useSettingsStore = defineStore('settings', {
  state: () => ({
    user: {
      name: '用户名',
      phone: '1101111111',
      lastTime: (new Date()).toLocaleString(),
    },
  }),
  actions: {
    initSettings() {
      fetch(useGlobalStore().url + "/control/config", {
        method: 'GET'
      })
        .then(response => response.json())
        .then(data => {
          this.user = data
          this.user.lastTime = Date().toLocaleString()
        })
        .catch(error => {
          ElMessage({
            message: '无法获取配置信息，请检查服务器是否正常运行！',
            type: 'error'
          })
        })
    },
    changeUser() {
      const formUser = reactive({
        name: '',
        phone: '',
      })
      ElMessageBox({
        title: '请输入您的信息',
        customClass: "user-change-form",
        message:
          h(ElForm,
            { labelWidth: "auto", labelPosition: "left" },
            () => [
              h(ElFormItem, { label: "用户名", required: true }, () => {
                return h(ElInput, { modelValue: formUser.name, 'onUpdate:modelValue': name => formUser.name = name }, null)
              }),
              h(ElFormItem, { label: "联系方式", required: true }, () => {
                return h(ElInput, { modelValue: formUser.phone, "onUpdate:modelValue": phone => formUser.phone = phone }, null)
              }),
            ]),
        showCancelButton: true,
        confirmButtonText: '确认',
        cancelButtonText: '取消',
      }).then(() => {
        this.user = {
          name: formUser.name,
          phone: formUser.phone,
          lastTime: new Date().toLocaleString()
        }
        ElMessage({
          type: 'success',
          message: '用户更改成功',
        })
      })
        .catch(() => {
          ElMessage({
            type: 'info',
            message: '用户更改取消',
          })
        })
    }

  }
})