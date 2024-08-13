import { defineStore } from 'pinia'
import { ref, h, reactive } from 'vue'
import { ElMessage, ElMessageBox, ElForm, ElFormItem, ElInput } from 'element-plus'

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
    totalCount: 0,
    pageSize: 5,
    currentPage: 1
  }),
  actions: {
    updateMeta() {
      fetch(useGlobalStore().url + "/db/data/meta", {
        method: 'GET'
      })
        .then(response => response.json())
        .then(data => {
          this.columns = data.columns
          this.columnsToFill = data.columns_to_fill
          this.colunmsShowSelected = data.columns
          this.totalCount = data.total_count
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