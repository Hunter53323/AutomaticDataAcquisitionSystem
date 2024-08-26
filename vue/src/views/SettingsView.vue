<script setup>
import { ref, onMounted, h } from 'vue'
import ProtocolsSetting from '@/components/settings/ProtocolsSetting.vue'
import MonitorSetting from '@/components/settings/MonitorSetting.vue'
import UserSetting from '@/components/settings/UserSetting.vue'
import DatabaseSetting from '@/components/settings/DatabaseSetting.vue'
import DeviceSetting from '@/components/settings/DeviceSetting.vue'
import { useDashboardStore, useSettingsStore, useDBStore, useGlobalStore } from '@/stores/global'
import CollectorSetting from '@/components/settings/CollectorSetting.vue'
import ProtocolSelectionBox from '@/components/settings/ProtocolSelectionBox.vue'
import ProtocolDelBox from '@/components/settings/ProtocolDelBox.vue'
import { ElMessageBox, ElMessage } from 'element-plus'

const global = useGlobalStore()
const dashboard = useDashboardStore()
const settings = useSettingsStore()
const db = useDBStore()

const activeNames = ref(['1'])

dashboard.initList()
dashboard.updateDeviceState()
settings.updateProtocol()
settings.updateConf()
settings.updateDefined()
settings.updateUser()
settings.updateSteady()
db.updateMeta()

const saveConfToDB = () => {
  // activeNames.value.push(driver == 'FanDriver' ? '1' : '2')
  ElMessageBox.prompt("请输入配置名称", {
    title: "保存配置至数据库",
    showCancelButton: true,
    confirmButtonText: '确定',
    cancelButtonText: '取消',
  })
    .then(({ value }) => {
      fetch(global.url + '/control/configsavev2?config_name=' + value, {
        method: 'POST'
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.status != true) {
            throw new Error(data.error)
          }
          settings.updateProtocol()
          ElMessage.success("成功保存配置 " + value + " 至数据库")
        })
        .catch((e) => {
          ElMessage.error("保存配置" + value + "失败")
        })
    })
    .catch((e) => {
      console.log(e)
      ElMessage.info('已取消对配置的保存')
    })
}


const delConfFromDB = () => {
  const choice = ref()
  ElMessageBox({
    title: "从数据库删除配置",
    message: h(ProtocolDelBox, {
      modelValue: choice, 'onUpdate:modelValue': (val) => choice.value = val
    }),
    showCancelButton: true,
    confirmButtonText: '确定',
    cancelButtonText: '取消',
  })
    .then(({ value }) => {
      fetch(global.url + '/control/configsavev2?config_id=' + choice.value, {
        method: 'DELETE'
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.status != true) {
            throw new Error(data.error)
          }
          settings.updateProtocol()
          ElMessage.success("成功从数据库删除配置 " + choice.value)
        })
        .catch((e) => {
          ElMessage.error("从数据库删除配置" + choice.value + "失败")
        })
    })
    .catch((e) => {
      ElMessage.info('已取消对配置的删除')
    })
}


const loadConfFromDB = () => {
  const choice = ref()
  ElMessageBox({
    title: "从数据库加载配置",
    message: h(ProtocolSelectionBox, {
      modelValue: choice, 'onUpdate:modelValue': (val) => choice.value = val
    }),
    showCancelButton: true,
    confirmButtonText: '确定',
    cancelButtonText: '取消',
  })
    .then(({ value }) => {
      fetch(global.url + '/control/configsavev2?config_id=' + choice.value, {
        method: 'PUT'
      })
        .then((response) => response.json())
        .then((data) => {
          if (data.status != true) {
            throw new Error(data.error)
          }
          settings.updateProtocol()
          dashboard.initList()
          settings.updateConf()
          settings.updateDefined()
          settings.updateUser()
          settings.updateSteady()
          db.updateMeta()
          ElMessage.success("成功加载配置 " + choice.value)
        })
        .catch((e) => {
          ElMessage.error("加载配置" + choice.value + "失败")
        })
    })
    .catch((e) => {
      ElMessage.info('已取消对配置的加载')
    })

}



</script>

<template>
  <el-button size="" type="primary" @click="saveConfToDB()" class="bntProtocol">
    保存配置至数据库
  </el-button>
  <el-divider direction="vertical" />
  <el-button size="" type="primary" @click="loadConfFromDB()" class="bntProtocol">
    从数据库加载配置
  </el-button>
  <el-divider direction="vertical" />
  <el-button size="" type="primary" @click="delConfFromDB()" class="bntProtocol">
    从数据库删除配置
  </el-button>
  <el-collapse v-model="activeNames" accordion>
    <el-collapse-item name="1">
      <template #title>
        <div class="collapse-title">设备配置</div>
      </template>
      <DeviceSetting />
    </el-collapse-item>
    <el-collapse-item name="2">
      <template #title>
        <div class="collapse-title">通讯协议</div>
      </template>
      <el-row>
        <el-col :span="24">
          <ProtocolsSetting />
        </el-col>
      </el-row>
    </el-collapse-item>

    <el-collapse-item name="3">
      <template #title>
        <div class="collapse-title">自动数采</div>
      </template>
      <CollectorSetting />
    </el-collapse-item>

    <!-- <el-collapse-item name="4">
      <template #title>
        <div class="collapse-title">监控面板</div>
      </template>
      <MonitorSetting />
    </el-collapse-item> -->

    <el-collapse-item name="5">
      <template #title>
        <div class="collapse-title">人员信息</div>
      </template>
      <UserSetting />
    </el-collapse-item>

    <el-collapse-item name="6">
      <template #title>
        <div class="collapse-title">数据库</div>
      </template>
      <DatabaseSetting />
    </el-collapse-item>
  </el-collapse>
</template>

<style>
.collapse-title {
  font-size: 20px;
}

.collapse-son .el-collapse-item__header {
  font-size: 16px;
}

.el-collapse-item__content {
  padding: 0;
}


.bntProtocol {
  margin: 0 0 10px 0;
}
</style>