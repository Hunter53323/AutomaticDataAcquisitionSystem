<script setup lang="js">
import { ref, onMounted, reactive, watch, computed, unref, toRaw, h } from 'vue'
import { useGlobalStore, useSettingsStore } from '@/stores/global';
import { ElMessage, ElMessageBox } from 'element-plus';
import { Close } from '@element-plus/icons-vue'
import DataModifyBox from '@/components/settings/DataModifyBox.vue'
import ProtocolSelectionBox from '@/components/settings/ProtocolSelectionBox.vue'
import DataAddBox from '@/components/settings/DataAddBox.vue';
import BreakdownAddBox from '@/components/settings/BreakdownAddBox.vue';
import BreakdownModifyBox from '@/components/settings/BreakdownModifyBox.vue';

const settings = useSettingsStore()
const global = useGlobalStore()

const loadConfFromDB = (driver) => {
  activeNames.value.push(driver == 'FanDriver' ? '1' : '2')
  const choice = ref()
  ElMessageBox({
    title: "从数据库加载配置",
    message: h(ProtocolSelectionBox, {
      driver: driver, modelValue: choice, 'onUpdate:modelValue': (val) => choice.value = val
    }),
    showCancelButton: true,
    confirmButtonText: '确定',
    cancelButtonText: '取消',
  })
    .then(({ value }) => {
      fetch(global.url + '/control/configsave?driver_name=' + driver + '&config_id=' + choice.value, {
        method: 'PUT'
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.status != true) {
            throw new Error(data.error)
          }
          settings.updateProtocol()
          ElMessage.success("成功加载 " + (driver == 'FanDriver' ? '被测设备 ' : '测试设备 ') + "的配置")
        })
        .catch((e) => {
          ElMessage.error("加载 " + (driver == 'FanDriver' ? '被测设备 ' : '测试设备 ') + "的配置失败")
        })
    })
    .catch((e) => {
      ElMessage.info('已取消对 ' + (driver == 'FanDriver' ? '被测设备 ' : '测试设备 ') + '配置的加载')
    })

}

const saveConfToDB = (driver) => {
  activeNames.value.push(driver == 'FanDriver' ? '1' : '2')
  ElMessageBox.prompt("请输入配置名称", {
    title: "保存配置至数据库",
    showCancelButton: true,
    confirmButtonText: '确定',
    cancelButtonText: '取消',
  })
    .then(({ value }) => {
      fetch(global.url + '/control/configsave?driver_name=' + driver + '&config_name=' + value, {
        method: 'POST'
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.status != true) {
            throw new Error(data.error)
          }
          settings.updateProtocol()
          ElMessage.success("成功保存 " + (driver == 'FanDriver' ? '被测设备 ' : '测试设备 ') + "的配置")
        })
        .catch((e) => {
          ElMessage.error("保存 " + (driver == 'FanDriver' ? '被测设备 ' : '测试设备 ') + "的配置失败")
        })
    })
    .catch((e) => {
      ElMessage.info('已取消对 ' + (driver == 'FanDriver' ? '被测设备 ' : '测试设备 ') + '配置的保存')
    })
}

const delData = (driver, key, index) => {
  let tmp
  if (driver == 'FanDriver') {
    tmp = formFan[key].data
  } else {
    tmp = formTest[key].data
  }
  tmp.splice(index, 1)
  for (let i = index; i < tmp.length; i++) {
    tmp[i].index--
  }
  ElMessage.success('已删除 ' + (driver == 'FanDriver' ? '被测设备 ' : '测试设备 ') + ' 协议 ' + formTitle[driver][key] + ' 的数据' + (index + 1) + ' ，请保存配置至数据库或加载配置至设备')
}

const subObj = ((obj, arr) => {
  const res = {}
  try {
    arr.forEach(key => {
      if (obj[key]) {
        res[key] = obj[key]
      } else {
        res[key] = 0
      }
    })
  } catch (error) {
  }
  return res
})

const activeNames = ref(['1'])

const formColHeader = {
  FanDriver: {
    header: '帧头',
    addr: '地址',
    cmd: '功能码',
    tail: '地址'
  },
  TestDevice: {

  }
}

const formTitle = {
  FanDriver: {
    ack_control_f: '控制回复',
    ack_query_f: '查询回复',
    control_f: '控制指令',
    query_f: '查询指令'
  },
  TestDevice: {
    rev_f: '接收指令'
  }
}
const formFan = reactive({
  ack_control_f: {
    addr: "",
    cmd: "",
    data: [],
    header: "",
    tail: ""
  },
  ack_query_f: {
    addr: "",
    cmd: "",
    data: [],
    header: "",
    tail: ""
  },
  control_f: {
    addr: "",
    cmd: "",
    data: [],
    header: "",
    tail: ""
  },
  query_f: {
    addr: "",
    cmd: "",
    data: [],
    header: "",
    tail: ""
  },
})
const formTest = reactive({
  rev_f: {
    data: [],
  }
})


const addBreakdown = (driver, key) => {
  let tmp
  if (driver == 'FanDriver') {
    tmp = formFan[key].data
  } else {
    tmp = formTest[key].data
  }
  const formAdd = reactive({
    name: '故障',
    breakdown: ['', '', '', '', '', '', '', ''],
    formula: '',
    inv_formula: '',
    index: 0,
    size: 1,
    type: 'bit8',
    raw_data: 0,
    real_data: 0,
  })
  ElMessageBox({
    title: '向  ' + formTitle[driver][key] + ' 添加 新的故障',
    message: h(BreakdownAddBox, { modelValue: formAdd, 'onUpdate:modelValue': (val) => formAdd = val }),
    showCancelButton: true,
    confirmButtonText: '确定',
    cancelButtonText: '取消',
  })
    .then(() => {
      if (tmp.length == 0) {
        formAdd.index = 1
      } else {
        formAdd.index = tmp.at(-1).index + 1
      }
      tmp.push(formAdd)
      ElMessage.success('已向 ' + (driver == 'FanDriver' ? '被测设备 ' : '测试设备 ') + ' 协议 ' + formTitle[driver][key] + ' 添加 ' + formAdd.name + ' ，请保存配置至数据库或加载配置至设备')
    })
    .catch(() => {
      ElMessage.info('已取消对 ' + (driver == 'FanDriver' ? '被测设备 ' : '测试设备 ') + ' 协议 ' + formTitle[driver][key] + ' 的 故障添加')
    })

}

const modifyBreakdown = (driver, key, index) => {
  let tmp
  if (driver == 'FanDriver') {
    tmp = formFan[key].data[index]
  } else {
    tmp = formTest[key].data[index]
  }
  const formModify = reactive({
    name: tmp.name,
    breakdown: tmp.breakdown,
    size: tmp.size,
    type: tmp.type,
  })
  ElMessageBox({
    title: '修改测试设备协议  ' + formTitle[driver][key] + ' 的 ' + tmp.name,
    message: h(BreakdownModifyBox, { modelValue: formModify, 'onUpdate:modelValue': (val) => formModify = val }),
  })
    .then(() => {
      tmp.formula = formModify.formula
      tmp.name = formModify.name
      // tmp.inv_formula = formModify.inv_formula
      tmp.index = formModify.index
      ElMessage.success('已修改 ' + (driver == 'FanDriver' ? '被测设备 ' : '测试设备 ') + ' 协议 ' + formTitle[driver][key] + ' 的 ' + tmp.name + ' ，请保存配置至数据库或加载配置至设备')
    })
    .catch(() => {
      ElMessage.info('已取消对 ' + (driver == 'FanDriver' ? '被测设备 ' : '测试设备 ') + ' 协议 ' + formTitle[driver][key] + ' 的 ' + tmp.name + ' 的修改')
    })

}

const loadConf = (driver, key) => {
  let tmp
  if (driver == 'FanDriver') {
    tmp = formFan
  } else {
    tmp = formTest
  }
  tmp = Object.assign({}, tmp)
  for (let key in tmp) {
    tmp[key]['data'].forEach((item) => {
      item.formula = item.formula.replace('真实数据', "real_data")
      item.formula = item.formula.replace('原始数据', "raw_data")
      item.inv_formula = item.inv_formula.replace('真实数据', "real_data")
      item.inv_formula = item.inv_formula.replace('原始数据', "raw_data")
    })
  }
  fetch(global.url + '/control/deviceset?driver_name=' + driver, {
    method: 'PUT',
    body: JSON.stringify(subObj(tmp, [key])),
    headers: {
      'Content-Type': 'application/json'
    }
  })
    .then((response) => response.json())
    .then((data) => {
      if (data.status != true) {
        throw new Error(data.error)
      }
      settings.updateProtocol()
      ElMessage.success("成功加载 " + (driver == 'FanDriver' ? '被测设备 的 ' : '测试设备 的 ') + formTitle[driver][key] + " 的配置")
    })
    .catch((e) => {
      ElMessage.error("无法加载 " + (driver == 'FanDriver' ? '被测设备 的 ' : '测试设备 的 ') + formTitle[driver][key] + " 的配置")
    })

}

const modifyOthers = (driver, key, target) => {
  let tmp
  if (driver == 'FanDriver') {
    tmp = formFan[key]
  } else {
    tmp = formTest[key]
  }
  ElMessageBox.prompt("请输入更新值", {
    title: "修改测试设备协议 " + formTitle[driver][key] + " 的 " + formColHeader[driver][target],
    showCancelButton: true,
    confirmButtonText: '确定',
    cancelButtonText: '取消',
  })
    .then(({ value }) => {
      tmp[target] = value
      ElMessage.success('已修改 ' + (driver == 'FanDriver' ? '被测设备 ' : '测试设备 ') + ' 协议 ' + formTitle[driver][key] + ' 的 ' + formColHeader[driver][target] + ' ，请保存配置至数据库或加载配置至设备')
    })
    .catch(() => {
      ElMessage.success('已取消对 ' + (driver == 'FanDriver' ? '被测设备 ' : '测试设备 ') + ' 协议 ' + formTitle[driver][key] + ' 的 ' + formColHeader[driver][target] + ' 的修改')
    })
}

const modifyData = (driver, key, index) => {
  let tmp
  if (driver == 'FanDriver') {
    tmp = formFan[key].data[index]
  } else {
    tmp = formTest[key].data[index]
  }
  const formModify = reactive({
    name: tmp.name,
    formula: tmp.formula,
    // inv_formula: tmp.inv_formula,
    index: tmp.index,
    size: tmp.size,
    type: tmp.type,
  })
  ElMessageBox({
    title: '修改测试设备协议  ' + formTitle[driver][key] + ' 的 ' + tmp.name,
    message: h(DataModifyBox, {
      modelValue: formModify,
      'onUpdate:modelValue': (val) => formModify = val,
      driver: driver
    }),
    showCancelButton: true,
    confirmButtonText: '确定',
    cancelButtonText: '取消',
  }).then(() => {
    tmp.name = formModify.name
    tmp.size = formModify.size
    tmp.type = formModify.type
    tmp.formula = formModify.formula
    // tmp.inv_formula = formModify.inv_formula
    tmp.index = formModify.index
    ElMessage.success('已修改 ' + (driver == 'FanDriver' ? '被测设备 ' : '测试设备 ') + ' 协议 ' + formTitle[driver][key] + ' 的 ' + tmp.name + ' ，请保存配置至数据库或加载配置至设备')
  }).catch(() => {
    ElMessage.info('已取消对 ' + (driver == 'FanDriver' ? '被测设备 ' : '测试设备 ') + ' 协议 ' + formTitle[driver][key] + ' 的 ' + tmp.name + ' 的修改')
  })
}

const addData = (driver, key) => {
  let tmp
  if (driver == 'FanDriver') {
    tmp = formFan[key].data
  } else {
    tmp = formTest[key].data
  }
  const formAdd = reactive({
    name: '',
    breakdown: [],
    formula: '真实数据=原始数据',
    inv_formula: '',
    index: 0,
    size: (driver == 'FanDriver' ? 2 : 4),
    type: (driver == 'FanDriver' ? 'int16' : 'float'),
    raw_data: 0,
    real_data: 0,
  })
  ElMessageBox({
    title: '向  ' + formTitle[driver][key] + ' 添加 新的数据',
    message: h(DataAddBox, {
      modelValue: formAdd,
      'onUpdate:modelValue': (val) => formAdd = val,
      driver: driver
    }),
    showCancelButton: true,
    confirmButtonText: '确定',
    cancelButtonText: '取消',
  }).then(() => {
    if (tmp.length == 0) {
      formAdd.index = 1
    } else {
      formAdd.index = tmp.at(-1).index + 1
    }
    tmp.push(formAdd)
    ElMessage.success('已向 ' + (driver == 'FanDriver' ? '被测设备 ' : '测试设备 ') + ' 协议 ' + formTitle[driver][key] + ' 添加 ' + formAdd.name + ' ，请保存配置至数据库或加载配置至设备')
  }).catch((e) => {
    ElMessage.info('已取消对 ' + (driver == 'FanDriver' ? '被测设备 ' : '测试设备 ') + ' 协议 ' + formTitle[driver][key] + ' 的数据添加')
  })


}

watch(() => settings.protocol['FanDriver'], (newProtocal) => {
  formFan.control_f = JSON.parse(JSON.stringify(newProtocal.control_f))
  formFan.query_f = JSON.parse(JSON.stringify(newProtocal.query_f))
  formFan.ack_control_f = JSON.parse(JSON.stringify(newProtocal.ack_control_f))
  formFan.ack_query_f = JSON.parse(JSON.stringify(newProtocal.ack_query_f))
  for (let key in formFan) {
    formFan[key]['data'].forEach((item) => {
      item.formula = item.formula.replace('real_data', "真实数据")
      item.formula = item.formula.replace('raw_data', "原始数据")
      item.inv_formula = item.inv_formula.replace("real_data", "真实数据")
      item.inv_formula = item.inv_formula.replace("raw_data", "原始数据")
    })
  }
}, { deep: true })

watch(() => settings.protocol['TestDevice'], (newProtocal) => {
  formTest.rev_f = JSON.parse(JSON.stringify(newProtocal.rev_f))
  for (let key in formTest) {
    formTest[key]['data'].forEach((item) => {
      item.formula = item.formula.replace('real_data', "真实数据")
      item.formula = item.formula.replace('raw_data', "原始数据")
      item.inv_formula = item.inv_formula.replace("real_data", "真实数据")
      item.inv_formula = item.inv_formula.replace("raw_data", "原始数据")
    })
  }
}, { deep: true })

</script>

<template>

  <div class="protocol-desc">
    <el-collapse v-model="activeNames">
      <el-collapse-item name="1" class="collapse-son">
        <template #title>
          <div>被测设备协议</div>
          <span v-show="activeNames.some(item => item === '1')">
            <el-divider direction="vertical" />
            <el-button size="small" type="primary" @click="saveConfToDB('FanDriver')"
              class="bntProtocol">保存配置至数据库</el-button>
            <el-divider direction="vertical" />
            <el-button size="small" type="primary" @click="loadConfFromDB('FanDriver')"
              class="bntProtocol">从数据库加载配置</el-button>
          </span>
        </template>
        <div v-for="value, key in formFan" class="desc-div">
          <el-descriptions direction="vertical" :column="12" border>
            <template #title>
              {{ formTitle.FanDriver[key] }}
              <el-divider direction="vertical" />
              <el-button class="bntProtocol" size="small" type="primary" @click="loadConf('FanDriver', key)" text
                bg>加载配置</el-button>
              <el-divider direction="vertical" />
              <el-button class="bntProtocol" size="small" type="primary" @click="addData('FanDriver', key)" text
                bg>添加数据</el-button>
              <el-divider direction="vertical" />
              <el-button class="bntProtocol" size="small" type="primary" @click="addBreakdown('FanDriver', key)" text
                bg>添加故障</el-button>
            </template>
            <el-descriptions-item align="center" v-for="(value_col, key_col) in formColHeader['FanDriver']"
              :label="value_col" label-align="center" width="100px">
              <el-button link class="bnt-item" @click="modifyOthers('FanDriver', key, key_col)">
                {{ value[key_col] }}
              </el-button>
            </el-descriptions-item>
            <el-descriptions-item align="center" label="数据" label-align="center" v-show="!value.data.length">
              <el-button link class="bnt-item">
                无
              </el-button>
            </el-descriptions-item>

            <el-descriptions-item align="center" v-for="dataItem, index in value.data" label-align="center">
              <template #label>
                {{ '数据' + (index + 1) }}
                <el-button :icon="Close" link class="del-bnt" @click="delData('FanDriver', key, index)"></el-button>
              </template>
              <el-popover placement="bottom" :title="dataItem.name" trigger="hover" width="450px">
                <template #reference>
                  <el-button link class="bnt-item" @click="dataItem.name.includes('故障') ? modifyBreakdown('FanDriver', key,
                    index) : modifyData('FanDriver', key, index)">
                    {{ dataItem.name }}
                  </el-button>
                </template>
                <template #default>
                  <div v-show="!dataItem.name.includes('故障')">计算公式: {{ dataItem.formula }}</div>
                  <div v-show="dataItem.name.includes('故障')">映射关系: {{ dataItem.breakdown }}</div>
                  <!-- <div>反解公式: {{ dataItem.inv_formula }}</div> -->
                  <div>序号: {{ dataItem.index }}</div>
                  <div>大小: {{ dataItem.size }} Bit</div>
                  <div>类型: {{ dataItem.type }}</div>
                </template>
              </el-popover>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-collapse-item>

      <el-collapse-item name="2" class="collapse-son">
        <template #title>
          <div>测试设备协议</div>
          <span v-show="activeNames.some(item => item === '2')">
            <el-divider direction="vertical" />
            <el-button size="small" type="primary" @click="saveConfToDB('TestDevice')" class="bntProtocol">
              保存配置至数据库
            </el-button>
            <el-divider direction="vertical" />
            <el-button size="small" type="primary" @click="loadConfFromDB('TestDevice')" class="bntProtocol">
              从数据库加载配置
            </el-button>
          </span>
        </template>

        <div v-for="value, key in formTest" class="desc-div">
          <el-descriptions direction="vertical" :column="12" border>
            <template #title>
              {{ formTitle.TestDevice[key] }}
              <el-divider direction="vertical" />
              <el-button class="bntProtocol" size="small" type="primary" @click="loadConf('TestDevice', key)" text bg>
                加载配置
              </el-button>
              <el-divider direction="vertical" />
              <el-button class="bntProtocol" size="small" type="primary" @click="addData('TestDevice', key)" text bg>
                添加数据
              </el-button>
            </template>

            <el-descriptions-item align="center" label="数据" label-align="center" v-show="!value.data.length">
              <el-button link class="bnt-item">
                无
              </el-button>
            </el-descriptions-item>

            <el-descriptions-item align="center" v-for="dataItem, index in value.data" label-align="center">
              <template #label>
                {{ '数据' + (index + 1) }}
                <el-button :icon="Close" link class="del-bnt" @click="delData('TestDevice', key, index)"></el-button>
              </template>
              <el-popover placement="bottom" :title="dataItem.name" trigger="hover" width="450px">
                <template #reference>
                  <el-button link class="bnt-item" @click="modifyData('TestDevice', key, index)">
                    {{ dataItem.name }}
                  </el-button>
                </template>
                <template #default>
                  <div>计算公式: {{ dataItem.formula }}</div>
                  <!-- <div>反解公式: {{ dataItem.inv_formula }}</div> -->
                  <div>序号: {{ dataItem.index }}</div>
                  <div>大小: {{ dataItem.size }} Bit</div>
                  <div>类型: {{ dataItem.type }}</div>
                </template>
              </el-popover>
            </el-descriptions-item>
          </el-descriptions>
        </div>
      </el-collapse-item>
    </el-collapse>
  </div>

</template>


<style scoped>
.desc-div {
  margin: 10px 0;
}

.protocol-desc :deep(.el-descriptions__title) {
  font-weight: normal;
  font-size: 14px;
}

.bntProtocol {
  margin: 0;
}

.del-bnt {
  margin: 0;
}
</style>