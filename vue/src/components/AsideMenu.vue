<script lang="ts" setup>
import { ref } from 'vue'
import {
  Document,
  Menu as IconMenu,
  Location,
  Setting,
} from '@element-plus/icons-vue'
import { useDashboardStore } from '@/stores/global';

const dashboard = useDashboardStore()

const judgeShow = () => {
  return dashboard.isFanRunning || dashboard.isTestRunning || dashboard.isAutoCollecting || dashboard.isFanConnected || dashboard.isTestConnected
}

</script>


<template>
  <el-menu default-active="/" class="el-menu-vertical-demo" :router="true">
    <el-menu-item index="/">
      <el-icon>
        <location />
      </el-icon>
      <template #title>仪表盘</template>
    </el-menu-item>
    <el-menu-item index="/database">
      <el-icon>
        <icon-menu />
      </el-icon>
      <template #title>数据库</template>
    </el-menu-item>
    <el-menu-item index="/settings" :disabled="judgeShow()">
      <el-icon>
        <setting />
      </el-icon>
      <template #title>配置</template>
    </el-menu-item>
  </el-menu>
</template>


<style>
.el-menu-vertical-demo:not(.el-menu--collapse) {
  width: 150px;
  height: 85vh;
}
</style>