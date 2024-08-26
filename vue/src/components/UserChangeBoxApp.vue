<script setup lang="js">
import { ref, onMounted } from 'vue'
import { useDashboardStore, useSettingsStore, useDBStore, useGlobalStore } from '@/stores/global'
import { useRouter } from 'vue-router';
import { ElMessageBox, ElMessage } from 'element-plus';



const router = useRouter()
const global = useGlobalStore()
const dashboard = useDashboardStore()
const settings = useSettingsStore()
const db = useDBStore()
const formUser = defineModel()

const clickBnt = () => {
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
      ElMessageBox.close()
    })
    .catch(() => {
      settings.updateUser()
      ElMessage.error('用户更改失败')
      
      ElMessageBox.close()
    })
}

</script>

<template>
  <el-form labelWidth="auto" labelPosition="left">
    <el-form-item label="用户名">
      <el-input v-model="formUser.name"></el-input>
    </el-form-item>
    <el-form-item label="联系方式">
      <el-input v-model="formUser.email"></el-input>
    </el-form-item>
  </el-form>
  <div class="bnt-div">
    <el-button type="primary" @click="clickBnt">确认</el-button>
  </div>
</template>


<style scoped>
.bnt-div {
  display: flex;
  justify-content: flex-end;
}

.el-button {
  margin: 12px 0 0 0;
}
</style>
