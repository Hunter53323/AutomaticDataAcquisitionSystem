<script setup>
import { RouterLink, RouterView } from 'vue-router'
import AsideMenu from './components/AsideMenu.vue'
</script>

<template>
  <div class="common-layout">
    <el-container direction="horizontal">
      <el-aside width="200px">
        <AsideMenu />
      </el-aside>
      <el-main>
        <RouterView />
      </el-main>

    </el-container>
  </div>
</template>

<style scoped>
.common-layout .el-aside {
  color: var(--el-text-color-primary);
}

</style>
