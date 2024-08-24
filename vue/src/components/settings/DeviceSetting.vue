<script setup lang="js">
import { onMounted, reactive, ref, watch } from 'vue';
import { useGlobalStore, useSettingsStore } from '@/stores/global';
import { ElMessage, } from 'element-plus';

const global = useGlobalStore()
const settings = useSettingsStore()
const activeNames = ref(['1', '2'])

const formFan = reactive({
  cpu: '',
  port: '',
  baudrate: ''
})

const formTest = reactive({
  ip: '',
  port: ''
})

const uploadFanForm = () => {
  fetch(global.url + '/control/deviceset?config_item=normal&driver_name=FanDriver', {
    method: 'POST',
    body: JSON.stringify(formFan),
    headers: {
      'Content-Type': 'application/json'
    }
  })
    .then(data => data.json())
    .then(data => {
      if (data.status != true) {
        throw new Error()
      }
      settings.updateConf()
      ElMessage({
        type: 'success',
        message: '被测设备配置成功'
      })
    })
    .catch((e) => {
      ElMessage.error('被测设备配置失败')

    })
}

const uploadTestForm = () => {
  fetch(global.url + '/control/deviceset?config_item=normal&driver_name=TestDevice', {
    method: 'POST',
    body: JSON.stringify(formTest),
    headers: {
      'Content-Type': 'application/json'
    }
  })
    .then(data => data.json())
    .then(data => {
      if (data.status != true) {
        throw new Error()
      }
      settings.updateConf()
      ElMessage({
        type: 'success',
        message: '测试设备配置成功'
      })
    })
    .catch((e) => {
      ElMessage.error('测试设备配置失败')

    })
}

watch(() => [settings.fanConf, settings.testConf], ([newFan, newTest]) => {
  formFan.cpu = newFan.cpu
  formFan.port = newFan.port
  formFan.baudrate = newFan.baudrate
  formTest.ip = newTest.ip
  formTest.port = newTest.port
}, { deep: true })

onMounted(() => {
  formFan.cpu = settings.fanConf.cpu
  formFan.port = settings.fanConf.port
  formFan.baudrate = settings.fanConf.baudrate
  formTest.ip = settings.testConf.ip
  formTest.port = settings.testConf.port
})

</script>

<template>
  <el-collapse v-model="activeNames" class="collapse-son">
    <el-collapse-item name="1">
      <template #title>
        <div>测试设备配置</div>
      </template>
      <el-form :model="formTest" label-width="90px" inline label-position="left">
        <el-row :gutter="20">
          <el-col :span="11">
            <el-form-item label="IP 地址配置" style="width:100%">
              <el-input v-model="formTest.ip" placeholder="输入被测设备IP地址">
              </el-input>
            </el-form-item>
          </el-col>
          <el-col :span="11">
            <el-form-item label="端口配置" style="width:100%">
              <el-input-number v-model="formTest.port" placeholder="输入被测设备端口" style="width:100%"
                :controls="false"></el-input-number>
            </el-form-item>
          </el-col>
          <el-col :span="2">
            <el-button type="success" @click="uploadTestForm">提交</el-button>
          </el-col>
        </el-row>
      </el-form>
    </el-collapse-item>

    <el-collapse-item name="2">
      <template #title>
        <div>被测设备配置</div>
      </template>
      <el-form :model="formTest" label-width="90px" inline label-position="left">
        <el-row :gutter="20">
          <el-col :span="7">
            <el-form-item label="CPU 配置" style="width:100%">
              <el-select v-model="formFan.cpu" placeholder="选择测试设备CPU">
                <el-option v-for="item in ['M0', 'M4']" :key="item" :label="item" :value="item" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="7">
            <el-form-item label="端口配置" style="width:100%">
              <el-select v-model="formFan.port" placeholder="选择测试设备端口">
                <el-option v-for="item in 254" :key="'COM' + item" :label="'COM' + item" :value="'COM' + item" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="8">
            <el-form-item label="波特率配置" style="width:100%">
              <el-select v-model="formFan.baudrate" placeholder="选择测试设备波特率">
                <el-option v-for="item in [300, 600, 1200, 2400, 4800, 9600, 19200, 38400, 57600, 115200]" :key="item"
                  :label="item" :value="item" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="2">
            <el-button type="success" @click="uploadFanForm">提交</el-button>
          </el-col>
        </el-row>
      </el-form>
    </el-collapse-item>
  </el-collapse>

</template>