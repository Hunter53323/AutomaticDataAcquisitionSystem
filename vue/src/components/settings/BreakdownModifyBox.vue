<script setup lang="js">
import { reactive, ref } from 'vue'

const form = defineModel()
</script>



<template>
  <el-form labelPosition="left" labelWidth="auto">
    <el-form-item required label="故障名称">
      <el-input v-model="form.name" placeholder="请输入故障名称"> </el-input>
    </el-form-item>
    <el-form-item v-for="(item, index) in form.breakdown" :label="'Bit ' + index">
      <el-input v-model="form.breakdown[index]"></el-input>
    </el-form-item>
    <el-form-item label="数据大小" required>
      <el-input v-model="form.size" disabled> </el-input>
    </el-form-item>
    <el-form-item label="数据类型" required>
      <el-input v-model="form.type" disabled> </el-input>
    </el-form-item>
  </el-form>

</template>