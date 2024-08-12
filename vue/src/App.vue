<script setup>
import { RouterLink, RouterView } from 'vue-router'
import AsideMenu from './components/AsideMenu.vue'
import { onMounted, h, reactive } from 'vue';
import { useDashboardStore, useSettingsStore } from '@/stores/global';
import { ElMessage, ElMessageBox, ElInput, ElForm, ElFormItem } from 'element-plus'


const dashboard = useDashboardStore()
const settings = useSettingsStore()


onMounted(() => {
  dashboard.initList()
  dashboard.initDeviceState()
  settings.initSettings()
})
</script>

<template>
  <div class="common-layout">
    <el-container>
      <el-header>
        <el-row>
          <el-col :span="12">
            <el-page-header :icon="null">
              <template #title>
                <div class="logo">
                  <img src="../static/logo.png" alt="logo" id="logo-img" />
                  国创中心数据采集系统
                </div>
              </template>
            </el-page-header>
          </el-col>
          <el-col :span="12">
            <div class="user-info">
              <el-button link @click="settings.changeUser">
                <el-text size="large">
                  {{ settings.user.name }}
                </el-text>
                <el-divider direction="vertical" class="info-divider" />
                <el-text size="large">
                  {{ settings.user.phone }}
                </el-text>
              </el-button>
            </div>
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

<style>
.common-layout .el-aside {
  color: var(--el-text-color-primary);
  padding: 20px 0;
}

.logo {
  display: flex;
  align-items: center;
  font-size: 30px;
  color: #2d2d2f;
  font-weight: bold;
}

.user-info {
  height: 70px;
  display: flex;
  justify-content: flex-end;
  align-items: center;
  color: #2d2d2f;
}

.info-divider {
  border-width: 2px;
  height: 20px;
  border-color: #6b6d71;
}

.el-page-header__header .el-divider {
  border-width: 0px;
}

#logo-img {
  width: 70px;
  height: 70px;
  margin-right: 10px;
}

.user-change-form .el-message-box__message {
  width: 100%;
}

.user-change-form .el-button {
  margin: 0 0 0 10px;
}
</style>
