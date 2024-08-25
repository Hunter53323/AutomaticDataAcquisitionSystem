<script setup>
import { RouterView } from 'vue-router'
import AsideMenu from './components/AsideMenu.vue'
import { useDashboardStore, useSettingsStore, useDBStore, useGlobalStore } from '@/stores/global'
import { onMounted, reactive, h } from '@vue/runtime-core';
import { ElMessageBox, ElMessage } from 'element-plus';
import UserChangeBox from './components/UserChangeBox.vue';
import { useRouter } from 'vue-router';


const router = useRouter()
const global = useGlobalStore()
const dashboard = useDashboardStore()
const settings = useSettingsStore()
const db = useDBStore()

const changeUser = () => {
  let formUser = reactive({
    name: '',
    email: '',
  })
  ElMessageBox({
    title: '请输入您的信息',
    customClass: "user-change-form",
    message:
      h(UserChangeBox, { modelValue: formUser, 'onUpdate:modelValue': value => formUser = value }),
    showCancelButton: true,
    confirmButtonText: '确认',
    cancelButtonText: '取消',
  }).then(() => {
    const formData = new FormData()
    formData.append('receiver_email', formUser.email)
    formData.append('receiver_name', formUser.name)
    fetch(global.url + '/collect/emailset', {
      method: 'POST',
      body: formData,
    })
      .then((data) => data.json())
      .then((data) => {
        if (data.status != true) {
          throw new Error()
        }
        settings.user = {
          name: formUser.name,
          email: formUser.email,
          lastTime: new Date().toLocaleString()
        }
        settings.updateUser()
        ElMessage.success('用户更改成功')
      })
      .catch(() => {
        settings.updateUser()
        ElMessage.error('用户更改失败')
      })
  })
    .catch(() => {
      ElMessage.info('用户更改取消')
    })
  router.push({
    name: 'dashboard'
  })
}



onMounted(() => {
  changeUser()
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
                  {{ settings.user.email }}
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

.el-message-box__message {
  width: 100%;
}

.el-message-box__btns .el-button {
  margin: 0 0 0 10px;
}

.el-message-box__content .el-form-item {
  margin-bottom: 12px;
}

.el-message-box__content .el-form-item:last-child {
  margin-bottom: 0;
}

.el-input-number .el-input__inner {
  text-align: left;
}
</style>
