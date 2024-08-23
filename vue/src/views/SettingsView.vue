<script setup>
import { ref, onMounted } from 'vue'
import ProtocolsSetting from '@/components/settings/ProtocolsSetting.vue'
import MonitorSetting from '@/components/settings/MonitorSetting.vue'
import UserSetting from '@/components/settings/UserSetting.vue'
import DatabaseSetting from '@/components/settings/DatabaseSetting.vue'
import DeviceSetting from '@/components/settings/DeviceSetting.vue'
import { useDashboardStore, useSettingsStore, useDBStore } from '@/stores/global'
import CollectorSetting from '@/components/settings/CollectorSetting.vue'

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
db.updateMeta()

</script>

<template>
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

    <el-collapse-item name="4">
      <template #title>
        <div class="collapse-title">监控面板</div>
      </template>
      <MonitorSetting />
    </el-collapse-item>

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
</style>