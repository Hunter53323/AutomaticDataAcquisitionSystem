<script setup lang="js">
import { ref, onMounted, reactive, watch, computed, unref, toRaw, h } from 'vue'
import { useGlobalStore, useSettingsStore } from '@/stores/global';
import { ElMessage, ElMessageBox } from 'element-plus';
import DataModifyBox from './DataModifyBox.vue';

const settings = useSettingsStore()
const global = useGlobalStore()

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

const activeNames = ref(['1', '2'])

const formColHeader = {
  FanDriver: {
    header: '帧头',
    addr: '地址',
    cmd: '功能码',
    tail: '地址'
  }
}

const formTitle = {
  FanDriver: {
    ack_control_f: '控制回复',
    ack_query_f: '查询回复',
    control_f: '控制指令',
    query_f: '查询指令'
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
const formTest = reactive({})

const loadConf = (driver, key) => {
  let tmp
  if (driver == 'FanDriver') {
    tmp = formFan
  } else {
    tmp = formTest
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
      ElMessage.success("成功加载 " + (driver == 'FanDriver' ? '被测设备 ' : '测试设备 ') + formTitle[driver][key] + " 的配置")
    })
    .catch((e) => {
      ElMessage.error("加载 " + (driver == 'FanDriver' ? '被测设备 ' : '测试设备 ') + formTitle[driver][key] + " 的配置")
    })

}

const modifyOthers = (driver, key, target) => {
  console.log(target)
  let tmp
  if (driver == 'FanDriver') {
    tmp = formFan[key]
  } else {
    tmp = formTest[key]
  }
  ElMessageBox.prompt("", {
    title: "修改测试设备协议 " + formTitle.FanDriver[key] + " 的 " + formColHeader[driver][target],
    showCancelButton: true,
    confirmButtonText: '确定',
    cancelButtonText: '取消',
  })
    .then(({ value }) => {
      tmp[target] = value
      ElMessage.success('已修改测试设备协议' + ' ' + formTitle.FanDriver[key] + ' 的 ' + formColHeader[driver][target] + ' ，请保存配置至数据库或加载配置至设备')
    })
    .catch(() => {
      ElMessage.success('已取消对测试设备协议 ' + formTitle.FanDriver[key] + ' 的 ' + formColHeader[driver][target] + ' 的修改')
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
    title: '修改测试设备协议  ' + formTitle.FanDriver[key] + ' 的 ' + tmp.name,
    message: h(DataModifyBox, { modelValue: formModify, 'onUpdate:modelValue': (val) => formModify = val }),
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
    ElMessage.success('已修改测试设备协议 ' + formTitle.FanDriver[key] + ' 的 ' + tmp.name + ' ，请保存配置至数据库或加载配置至设备')
  }).catch(() => {
    ElMessage.info('已取消对测试设备协议 ' + formTitle.FanDriver[key] + ' 的 ' + tmp.name + ' 的修改')
  })
}

watch(() => settings.protocol['FanDriver'], (newProtocal) => {
  formFan.control_f = JSON.parse(JSON.stringify(newProtocal.control_f))
  formFan.query_f = JSON.parse(JSON.stringify(newProtocal.query_f))
  formFan.ack_control_f = JSON.parse(JSON.stringify(newProtocal.ack_control_f))
  formFan.ack_query_f = JSON.parse(JSON.stringify(newProtocal.ack_query_f))
}, { deep: true })

// watch(() => settings.protocol['TestDevice'], (newProtocal) => {
//   formTest.control_f = newProtocal.control_f
//   formTest.query_f = newProtocal.query_fs
//   formTest.ack_control_f = newProtocal.ack_control_f
//   formTest.ack_query_f = newProtocal.ack_query_f
//   console.log(formFan.value)
// }, { deep: true })

</script>

<template>

  <div class="protocol-desc">
    <el-collapse v-model="activeNames">
      <el-collapse-item name="1" class="collapse-son">
        <template #title>
          <div>被测设备协议</div>
          <span v-show="'1' in activeNames">
            <el-divider direction="vertical" />
            <el-button size="small" type="primary">保存配置至数据库</el-button>
            <el-divider direction="vertical" />
            <el-button size="small" type="primary">从数据库加载配置</el-button>
          </span>
        </template>
        <div v-for="value, key in formFan" class="desc-div">
          <el-descriptions direction="vertical" :column="20" border>
            <template #title>
              {{ formTitle.FanDriver[key] }}
              <el-divider direction="vertical" />
              <el-button size="small" type="primary" @click="loadConf('FanDriver', key)" text bg>加载配置</el-button>
              <el-divider direction="vertical" />
              <el-button size="small" type="primary" @click="loadConf('FanDriver', key)" text bg>添加数据</el-button>
            </template>
            <template #extra>
            </template>
            <el-descriptions-item v-for="(value_col, key_col) in formColHeader['FanDriver']" :label="value_col"
              label-align="center" width="100px">
              <el-button link class="bnt-item" @click="modifyOthers('FanDriver', key, key_col)">
                {{ value[key_col] }}
              </el-button>
            </el-descriptions-item>
            <el-descriptions-item label="数据" label-align="center" v-show="!value.data.length">
              <el-button link class="bnt-item">
                无
              </el-button>
            </el-descriptions-item>
            <el-descriptions-item v-for="dataItem, index in value.data" :label="'数据' + (index + 1)"
              label-align="center">
              <el-popover placement="top" :title="dataItem.name" trigger="hover" width="450px">
                <template #reference>
                  <el-button link class="bnt-item" @click="modifyData('FanDriver', key, index)">
                    {{ dataItem.name }}
                  </el-button>
                </template>
                <template #default>
                  <div>计算公式: {{ dataItem.formula }}</div>
                  <div>反解公式: {{ dataItem.inv_formula }}</div>
                  <div>序号: {{ dataItem.index }}</div>
                  <div>大小: {{ dataItem.size }} Bits</div>
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
        </template>
      </el-collapse-item>
    </el-collapse>
  </div>

</template>


<style scoped>
.bnt-item {
  width: 100%;
}

.desc-div {
  margin: 10px 0;
}


.protocol-desc :deep(.el-descriptions__title) {
  font-weight: normal;
  font-size: 14px;
}
</style>