<script setup lang="ts">
import { useSettingsStore } from '@/stores/global';
import { User, Iphone, Clock, Bell } from '@element-plus/icons-vue'

const settings = useSettingsStore();

</script>

<template>
  <el-row :gutter="20">
    <el-col :span="22">
      <el-descriptions class="user-desc" :column="4" size="large" border>
        <el-descriptions-item>
          <template #label>
            <div class="innerLabel">
              <el-icon size="large" class="innerIcon">
                <user />
              </el-icon>
              用户名
            </div>
          </template>
          {{ settings.user.name }}
        </el-descriptions-item>
        <el-descriptions-item>
          <template #label>
            <div class="innerLabel">
            <el-icon size="large" class="innerIcon">
              <iphone />
            </el-icon>
            联系方式
            </div>
          </template>
          {{ settings.user.email }}
        </el-descriptions-item>
        <el-descriptions-item>
          <template #label>
            <div class="innerLabel">
              <el-icon size="large" class="innerIcon">
                <clock />
              </el-icon>
              登录时间
            </div>
          </template>
          {{ settings.user.lastTime }}
        </el-descriptions-item>
        <el-descriptions-item>
          <template #label>
            <div class="innerLabel">
              <el-icon size="large" class="innerIcon">
                <Bell />
              </el-icon>
              通知邮箱
            </div>
          </template>
          {{ settings.user.sender_email }}
        </el-descriptions-item>
      </el-descriptions>
    </el-col>
    <el-col :span="2">
      <el-button type="warning" @click="settings.changeUser" size="large">切换</el-button>
    </el-col>
  </el-row>
</template>

<style scoped>
.el-col-2 {
  display: flex;
  justify-content: center;
  align-items: center;
}
.innerLabel {
  display: flex;
  align-items: center;
}
.innerIcon {
  margin-right: 10px;
}
.user-desc {
  margin: 10px 0;
}
</style>