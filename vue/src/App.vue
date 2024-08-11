<script setup>
import { RouterLink, RouterView } from 'vue-router'
import AsideMenu from './components/AsideMenu.vue'
import { onMounted } from 'vue';
import { useDashboardStore } from '@/stores/global';

const dashboard = useDashboardStore()

dashboard.initList()
dashboard.initDeviceState()


</script>

<template>
  <div class="common-layout">
    <el-container>
      <el-header>
        <el-row type="flex" justify="space-between">
          <el-col :span="12">
            <h1>Vue3 Admin</h1>
          </el-col>
        </el-row>
      </el-header>
    </el-container>
    <el-container direction="horizontal">
      <el-aside width="150px">
        <AsideMenu />
      </el-aside>
      <el-container>
        <el-main>
          <RouterView />
        </el-main>
      </el-container>

    </el-container>
  </div>
</template>

<style scoped>
.common-layout .el-aside {
  color: var(--el-text-color-primary);
  padding: 20px 0;
}
</style>
