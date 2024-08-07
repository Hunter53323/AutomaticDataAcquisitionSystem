<script setup>
import { RouterLink, RouterView } from 'vue-router'
import AsideMenu from './components/AsideMenu.vue'
</script>

<template>
  <div class="common-layout">
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
