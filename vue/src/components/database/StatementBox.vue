<script setup lang="js">
import { ref, onMounted, reactive, watch, computed } from 'vue'
import { FolderOpened } from '@element-plus/icons-vue'

const form = defineModel()

</script>

<template>
  <el-form labelPosition="left" labelWidth="auto">
    <el-form-item label="导出文件名" required>
      <el-input v-model="form.filename" placeholder="请输入导出文件名"></el-input>
    </el-form-item>
    <el-form-item label="导出目录" required>
      <el-input v-model="form.filepath" placeholder="请选择导出目录">
        <template #suffix>
          <el-icon>
            <FolderOpened />
          </el-icon>
        </template>
      </el-input>
    </el-form-item>
    <el-form-item label="筛选条件" required>
      <el-input v-model="form.conditions" placeholder="请输入筛选条件"></el-input>
    </el-form-item>
  </el-form>

</template>