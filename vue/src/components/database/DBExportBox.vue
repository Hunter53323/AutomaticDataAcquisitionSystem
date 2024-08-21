<script setup lang="js">
import { ref, onMounted, reactive, watch, computed } from 'vue'
import { FolderOpened } from '@element-plus/icons-vue'

const form = defineModel()

const dirChoose = () => {
  try {
    var file = document.getElementById('file')
    file.click()
  }
  catch {
    //用户拒绝查看文件
    alert('访问失败')
  }
}

const fileChange = () => {
  // try {
  //   const fu = document.getElementById('file')
  //   if (fu == null) return
  //   form.filepath = fu.files[0].path
  //   console.log(fu.files[0].path)
  // } catch (error) {
  //   console.debug('choice file err:', error)
  // }
}

</script>

<template>
  <el-form labelPosition="left" labelWidth="auto">
    <el-form-item label="导出文件名" required>
      <el-input v-model="form.filename" placeholder="请输入导出文件名"></el-input>
    </el-form-item>
    <el-form-item label="导出目录" required>
      <el-input v-model="form.filepath" placeholder="请选择导出目录" multiple>
        <template #suffix>
          <input type="file" id="file" hidden @change="fileChange" webkitdirectory>
          <el-button :icon="FolderOpened" link @click="dirChoose">
          </el-button>
        </template>
      </el-input>
    </el-form-item>
    <el-form-item label="筛选条件">
      <el-input v-model="form.conditions" placeholder="请输入筛选条件"></el-input>
    </el-form-item>
  </el-form>

</template>
