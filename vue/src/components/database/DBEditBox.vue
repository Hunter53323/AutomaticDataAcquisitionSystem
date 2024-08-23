<script setup lang="js">
import { ref, onMounted, reactive, watch, computed } from 'vue'
const form = defineModel()

</script>

<template>
  <el-form>
    <el-form :model="form" label-width="auto">
      <el-form-item v-for="(value, key) in form" :label="key">
        <el-input v-model="form[key]" clearable />
      </el-form-item>
    </el-form>
  </el-form>

</template>