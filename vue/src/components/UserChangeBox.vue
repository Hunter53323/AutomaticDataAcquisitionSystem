<script setup lang="js">
import { ref, onMounted } from 'vue'

const formUser = defineModel()

</script>

<template>
  <el-form  labelWidth="auto" labelPosition="left" >
    <el-form-item label="用户名">
      <el-input v-model="formUser.name"></el-input>
    </el-form-item>
    <el-form-item label="联系方式">
      <el-input v-model="formUser.email"></el-input>
    </el-form-item>
  </el-form>
</template>


<style scoped></style>
