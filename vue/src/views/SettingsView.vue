<script setup>
import { ref, onMounted } from 'vue'
import ProtocolsSetting from '@/components/settings/ProtocolsSetting.vue'
import MonitorSetting from '@/components/settings/MonitorSetting.vue'
import StaffSetting from '@/components/settings/StaffSetting.vue'
import DatabaseSetting from '@/components/settings/DatabaseSetting.vue'

const activeNames = ref(['1'])
</script>

<template>
  <el-collapse v-model="activeNames">
    <el-collapse-item name="1">
      <template #title>
        <div class="collapse-title">通讯协议</div>
      </template>
      <el-row>
        <el-col :span="24">
          <ProtocolsSetting />
        </el-col>
      </el-row>
    </el-collapse-item>

    <el-collapse-item name="2">
      <template #title>
        <div class="collapse-title">监控面板</div>
      </template>
      <MonitorSetting />
    </el-collapse-item>

    <el-collapse-item name="3">
      <template #title>
        <div class="collapse-title">人员信息</div>
      </template>
      <StaffSetting />
    </el-collapse-item>

    <el-collapse-item name="4">
      <template #title>
        <div class="collapse-title">数据库</div>
      </template>
      <DatabaseSetting />
    </el-collapse-item>
  </el-collapse>
</template>

<style>
.collapse-title {
  font-size: 16px;
}
</style>