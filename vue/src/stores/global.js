import { defineStore } from 'pinia'
import { ref, h, reactive } from 'vue'
import { ElMessage, ElMessageBox, ElForm, ElFormItem, ElInput } from 'element-plus'
import DBExportBox from '@/components/database/DBExportBox.vue'
import StatementBox from '@/components/database/StatementBox.vue'
import DBEditBox from '@/components/database/DBEditBox.vue'
import DBAddBox from '@/components/database/DBAddBox.vue'
import UserChangeBox from '@/components/UserChangeBox.vue'
import { protocol } from 'socket.io-client'

export const useGlobalStore = defineStore('global', {
  state: () => {
    return {
      url: 'http://127.0.0.1:5000'
    }
  },
  actions: {
    getUnit(key) {
      return ''
      if (key.includes('转速')) {
        return 'rpm'
      } else if (key.includes('电流环')) {
        return ''
      } else if (key.includes('电流')) {
        return 'A'
      } else if (key.includes('电压')) {
        return 'V'
      } else if (key.includes('功率')) {
        return 'W'
      } else if (key.includes('温度')) {
        return '°C'
      } else if (key.includes('湿度')) {
        return '%'
      } else {
        return ''
      }
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
        .catch(response => {
          ElMessage.error('无法获取数据库元数据，请检查数据库是否正常运行')
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
              ElMessage.error('数据删除失败')
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
          })
            .then(response => response.json())
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
              ElMessage.error('数据清除失败')
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
      let form = reactive({
        filename: '',
        ids_input: '',
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
          form.filename += '.csv'
          fetch(useGlobalStore().url + "/db/export", {
            method: 'POST',
            body: JSON.stringify(form),
            headers: {
              'Content-Type': 'application/json'
            }
          })
            .then(response => response.blob())
            .then(blob => {
              const url = window.URL.createObjectURL(blob);
              const link = document.createElement('a');
              link.href = url;
              link.setAttribute('download', form.filename);
              document.body.appendChild(link);
              link.click();
            })
            .catch((e) => {
              console.log(e)
              ElMessage.error('数据导出失败')
            })
        })
        .catch((e) => {
          console.log(e)
          ElMessage({
            type: 'info',
            message: '数据导出取消',
          })
        })

    },
    async handleStatementExport() {
      let form = reactive({
        filename: '',
        ids_input: '',
        draw_parameters: [],
        data_column: [],
        input_form: {
          "实验员姓名": "",
          "公司名称": ""
        }
      })
      this.columns.forEach((item) => {
        form.data_column.push([item])
      })
      ElMessageBox({
        title: '报表导出',
        message: h(StatementBox, { modelValue: form, 'onUpdate:modelValue': value => form = value, columns: this.columnsToFill }),
        customClass: "db-operation-box",
        showCancelButton: true,
        confirmButtonText: '确认',
        cancelButtonText: '取消',
      })
        .then(() => {
          let tmp = []
          form.draw_parameters.forEach((item) => {
            tmp.push(item[0])
          })
          form.draw_parameters = tmp
          tmp = []
          form.data_column.forEach((item) => {
            tmp.push(item[0])
          })

          form.data_column = tmp
          fetch(useGlobalStore().url + "/db/statement", {
            method: 'POST',
            body: JSON.stringify(form),
            headers: {
              'Content-Type': 'application/json'
            }
          })
            .then(response => response.blob())
            .then(blob => {
              const url = window.URL.createObjectURL(blob);
              const link = document.createElement('a');
              link.href = url;
              link.setAttribute('download', form.filename);
              document.body.appendChild(link);
              link.click();
            })
            .catch((e) => {
              ElMessage.error('报表导出失败')
            })
        })
        .catch((e) => {
          ElMessage({
            type: 'info',
            message: '报表导出取消',
          })
        })

    },
    async handleDBAdd() {
      let form = reactive({})
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
          body: JSON.stringify({ data_list: form }),
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
            ElMessage.error('数据添加失败')
          })
      })
        .catch(() => {
          ElMessage({
            type: 'info',
            message: '数据添加取消',
          })
        })
    },
    async handleDBEdit(id) {
      let form = reactive({})
      this.columnsToFill.forEach((column) => {
        form[column] = this.dbDataObjList.find((item) => item['ID'] == id)[column]
      })
      ElMessageBox({
        title: '编辑数据',
        message: h(DBEditBox, { modelValue: form, 'onUpdate:modelValue': value => form = value }),
        showCancelButton: true,
        customClass: "db-operation-box",
        confirmButtonText: '确认',
        cancelButtonText: '取消',
      }).then(() => {
        fetch(useGlobalStore().url + "/db/data", {
          method: 'PUT',
          body: JSON.stringify({
            ids: id, update_data: form
          }),
          headers: {
            'Content-Type': 'application/json'
          }
        }).then(response => response.json())
          .then(data => {
            if (data.status == 'error') {
              throw new Error(data.message)
            }
            this.dbDataUpdate()
            ElMessage.success('数据编辑成功')
          })
          .catch(response => {
            ElMessage.error('数据编辑失败')
          })
      })
        .catch(() => {
          ElMessage.info('数据编辑取消')
        })
    }
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
    autoCollectStatus: 1,
    dataObjList: {},
    dataShowSelected: {},
    paraList: [],
    paraShowSelected: [],
    dataList: [],
    graphClass: {
      "转速": [],
      "电流": [],
      "电压": [],
      "功率": [],
    },
  }),
  actions: {
    isReady() {
      console.log(this.isFanConnected, this.isTestConnected, this.isTestRunning)
      return this.isFanConnected && this.isTestConnected && this.isTestRunning
    },
    async initList() {
      fetch(useGlobalStore().url + "/control/data", {
        method: 'GET'
      })
        .then(response => response.json())
        .then(data => {
          this.dataObjList = Object.assign({}, data)
          this.dataShowSelected = Object.assign({}, this.dataObjList)
          this.dataList = [...data['FanDriver'], ...data['TestDevice']].filter((item) => item != "故障")
          this.graphClass = {
            "转速": [],
            "电流": [],
            "电压": [],
            "功率": [],
          }
          const tmpList = [...this.dataList, ...this.paraList]
          tmpList.forEach((item) => {
            if (item.includes('功率')) {
              this.graphClass['功率'].push(item)
            } else if (item.includes('电流环')) {

            } else if (item.includes('电流')) {
              this.graphClass['电流'].push(item)
            } else if (item.includes('电压')) {
              this.graphClass['电压'].push(item)
            } else if (item.includes('转速')) {
              this.graphClass['转速'].push(item)
            }
          })
          // console.log(this.graphClass)
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
    async updateDeviceState() {
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
    operationChoice: ['+', '-', '*', '/', '(', ')'],
    testConf: {
      ip: '',
      port: ''
    },
    fanConf: {
      cpu: '',
      port: '',
      baudrate: ''
    },
    definedColumns: {},
    protocol: {},
    protocolChoice: {},
    steadyConf: {}
  }),
  actions: {
    async updateSteady() {
      fetch(useGlobalStore().url + '/collect/steady_state_determination', {
        method: 'GET'
      })
        .then(data => data.json())
        .then(data => {
          this.steadyConf = data.value
        })
        .catch((e) => {
          ElMessage.error("无法获取 稳态判定参数 ，请检查服务器是否正常运行！")
        })
    },
    async updateProtocol() {
      // fetch(useGlobalStore().url + '/control/configsave?driver_name=FanDriver')
      //   .then(data => data.json())
      //   .then(data => {
      //     this.protocolChoice['FanDriver'] = data.value
      //   })
      //   .catch((e) => {
      //     ElMessage.error("无法获取 被测设备 协议配置 ，请检查服务器是否正常运行！")
      //   })
      // fetch(useGlobalStore().url + '/control/configsave?driver_name=TestDevice')
      //   .then(data => data.json())
      //   .then(data => {
      //     this.protocolChoice['TestDevice'] = data.value
      //   })
      //   .catch((e) => {
      //     ElMessage.error("无法获取 测试设备 协议配置 ，请检查服务器是否正常运行！")
      //   })

      fetch(useGlobalStore().url + '/control/configsavev2')
        .then(data => data.json())
        .then(data => {
          this.protocolChoice = data.value
        })
        .catch((e) => {
          ElMessage.error("无法获取配置 ，请检查服务器是否正常运行！")
        })
      fetch(useGlobalStore().url + "/control/deviceset?config_item=config&driver_name=FanDriver", {
        method: 'GET'
      })
        .then(response => response.json())
        .then(data => {
          this.protocol['FanDriver'] = data
        })
        .catch(error => {
          ElMessage({
            message: '无法获取 被测设备 协议配置 ，请检查服务器是否正常运行！',
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
            message: '无法获取 测试设备 协议配置 ，请检查服务器是否正常运行！',
            type: 'error'
          })
        })
    },
    async changeUser() {
      let formUser = reactive({
        name: '',
        email: '',
      })
      ElMessageBox({
        title: '请输入您的信息',
        customClass: "user-change-form",
        message:
          h(UserChangeBox, { modelValue: formUser, 'onUpdate:modelValue': value => formUser = value }),
        confirmButtonText: '确认',
        showConfirmButton: false,
        closeOnClickModal: false,
        closeOnPressEscape: false,
        "show-close": false
      })
      router.push({
        name: 'dashboard'
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
          this.fanConf.baudrate = data.baudrate
        })
        .catch((e) => {
          ElMessage.error("无法获取被测设备基本参数，请检查服务器是否正常运行！")
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