<script setup lang="js">
import { ref, onMounted, reactive, watch, computed } from 'vue'

const form = defineModel()


</script>

<template>
  <el-form labelPosition="left" labelWidth="auto">
    <el-form-item label="导出文件名">
      <el-input v-model="form.filename" placeholder="请输入导出文件名">
        <template #append>
          .csv
        </template>
      </el-input>
    </el-form-item>
    <el-form-item label="导出 ID">
      <el-input v-model="form.ids_input" placeholder="请输入导出 ID"></el-input>
    </el-form-item>
    <el-form-item label="筛选条件">
      <el-input v-model="form.conditions" placeholder="请输入筛选条件"></el-input>
    </el-form-item>
  </el-form>

</template>
