import { defineStore } from 'pinia'
import { ref, h, reactive } from 'vue'
import { ElMessage, ElMessageBox, ElForm, ElFormItem, ElInput } from 'element-plus'
import DBExportBox from '@/components/database/DBExportBox.vue'
import StatementBox from '@/components/database/StatementBox.vue'
import DBAddBox from '@/components/database/DBAddBox.vue'
import UserChangeBox from '@/components/UserChangeBox.vue'

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
    async updateMeta() {
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
    async dbDataUpdate() {
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
    async handleDBDelete(ids) {
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
    async handleDBExport() {
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
    async handleStatementExport() {
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
    async handleDBAdd() {
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
    remainCount: 0,
    successCount: 0,
    failCount: 0,
    isFanConnected: false,
    isTestConnected: false,
    isFanRunning: false,
    isTestRunning: false,
    isFanBreakDown: false,
    isTestBreakDown: false,
    isAutoCollecting: false,
    dataObjList: {},
    dataShowSelected: {},
    paraList: [],
    paraShowSelected: [],

  }),
  actions: {
    async initList() {
      fetch(useGlobalStore().url + "/control/data", {
        method: 'GET'
      })
        .then(response => response.json())
        .then(data => {
          this.dataObjList = Object.assign({}, data)
          this.dataShowSelected = Object.assign({}, this.dataObjList)
          useSettingsStore().varChoice = [...data['FanDriver'], ...data['TestDevice']].filter((item) => item != "故障")
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
    async initDeviceState() {
      fetch(useGlobalStore().url + '/control/state', {
        method: 'GET',
      })
        .then((response) => response.json())
        .then((data) => {
          this.isFanConnected = data.FanDriver['连接状态']
          this.isFanRunning = data.FanDriver['运行状态']
          this.isFanBreakDown = data.FanDriver['故障']
          this.isTestConnected = data.TestDevice['连接状态']
          this.isTestRunning = data.TestDevice['运行状态']
          this.isTestBreakDown = data.TestDevice['故障']
        })
        .catch(error => {
          ElMessage({
            message: '无法获取设备状态，请检查服务器是否正常运行！',
            type: 'error'
          })
        })
    },
    async updateCollectState() {
      fetch(useGlobalStore().url + "/collect/view")
        .then(response => response.json())
        .then(data => {
          ElMessage.success('数采状态更新成功')
          this.remainCount = data.remaining
          this.successCount = data.success
          this.failCount = data.fail
          this.isAutoCollecting = !data.complete
        })
        .catch(error => {
          ElMessage.error('无法获取数采状态，请检查服务器是否正常运行')
        });
    }
  }
})
export const useSettingsStore = defineStore('settings', {
  state: () => ({
    user: {
      name: '',
      email: '',
      sender_email: '',
      lastTime: (new Date()).toLocaleString(),
    },
    varChoice: [],
    operationChoice: ['+', '-', '*', '/', '(', ')'],
    testConf: {
      ip: '',
      port: ''
    },
    fanConf: {
      cpu: '',
      port: ''
    },
    definedColumns: {},
    protocol: {}
  }),
  actions: {
    async updateProtocol() {
      fetch(useGlobalStore().url + "/control/deviceset?config_item=config&driver_name=FanDriver", {
        method: 'GET'
      })
        .then(response => response.json())
        .then(data => {
          this.protocol['FanDriver'] = data
        })
        .catch(error => {
          ElMessage({
            message: '无法获取被测设备协议配置，请检查服务器是否正常运行！',
            type: 'error'
          })
        })
      fetch(useGlobalStore().url + "/control/deviceset?config_item=config&driver_name=TestDevice", {
        method: 'GET'
      })
        .then(response => response.json())
        .then(data => {
          this.protocol['TestDevice'] = data
        })
        .catch(error => {
          ElMessage({
            message: '无法获取测试设备协议配置，请检查服务器是否正常运行！',
            type: 'error'
          })
        })
    },
    async changeUser() {
      const formUser = reactive({
        name: '',
        email: '',
      })
      ElMessageBox({
        title: '请输入您的信息',
        customClass: "user-change-form",
        message:
          h(UserChangeBox, { modelValue: formUser, 'onUpdate:modelValue': value => formUser = value }),
        showCancelButton: true,
        confirmButtonText: '确认',
        cancelButtonText: '取消',
      }).then(() => {
        const formData = new FormData()
        formData.append('receiver_email', formUser.email)
        formData.append('receiver_name', formUser.name)
        fetch(useGlobalStore().url + '/collect/emailset', {
          method: 'POST',
          body: formData,
        })
          .then((data) => data.json())
          .then((data) => {
            if (data.status != true) {
              throw new Error()
            }
            this.user = {
              name: formUser.name,
              email: formUser.email,
              lastTime: new Date().toLocaleString()
            }
            this.updateUser()
            ElMessage({
              type: 'success',
              message: '用户更改成功',
            })
          })
          .catch(() => {

            this.updateUser()
            ElMessage({
              type: 'error',
              message: '用户更改失败',
            })
          })
      })
        .catch(() => {
          ElMessage({
            type: 'info',
            message: '用户更改取消',
          })
        })
    },
    async updateConf() {
      fetch(useGlobalStore().url + '/control/deviceset?config_item=normal&driver_name=TestDevice')
        .then(data => data.json())
        .then(data => {
          this.testConf.ip = data.ip
          this.testConf.port = data.port
        })
        .catch((e) => {
          ElMessage.error("无法获取测试设备基本参数，请检查服务器是否正常运行！")
        })
      fetch(useGlobalStore().url + '/control/deviceset?config_item=normal&driver_name=FanDriver')
        .then(data => data.json())
        .then(data => {
          this.fanConf.cpu = data.cpu
          this.fanConf.port = data.port
        })
        .catch((e) => {
          ElMessage.error("无法获取测试设备基本参数，请检查服务器是否正常运行！")
        })
    },
    async updateDefined() {
      fetch(useGlobalStore().url + '/control/custom_column')
        .then(data => data.json())
        .then(data => {
          this.definedColumns = data
        })
        .catch((e) => {
          ElMessage({
            message: '无法获取用户自定义数据列，请检查服务器是否正常运行！',
            type: 'error'
          })
        })
    },
    async updateUser() {
      fetch(useGlobalStore().url + '/collect/emailset')
        .then(data => data.json())
        .then(data => {
          this.user.sender_email = data.sender_mail
          this.user.email = data.receiver_email
          this.user.name = data.receiver_name
        })
        .catch((e) => {
          ElMessage({
            message: '无法获取用户自定义数据列，请检查服务器是否正常运行！',
            type: 'error'
          })
        })
    }
  }
})