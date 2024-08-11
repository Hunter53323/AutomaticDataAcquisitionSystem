<script setup lang="ts">
import { ref, onMounted, reactive, watch } from 'vue'

const form = reactive({
  header: 0,
  address: 0,
  code: 0,
  dataCount: 0,
  data: {},
  trailer: 0
})

watch(() => form.dataCount, (newVal, oldVal) => {
  for (let i = 1; i <= newVal; i++) {
    if (!form.data['data' + i]) {
      form.data['data' + i] = 0
    }
  }
  for (let i = newVal + 1; i <= oldVal; i++) {
    delete form.data['data' + i]
  }
}, { deep: true })

const onSubmit = () => {
  console.log(form)
}
</script>

<template>
  <el-form :model="form" label-width="auto" label-position="top" :inline="true" class="form-all">
    <el-form-item label="帧头">
      <el-input v-model="form.header" />
    </el-form-item>
    <el-form-item label="地址">
      <el-input v-model="form.address" />
    </el-form-item>
    <el-form-item label="命令码">
      <el-input v-model="form.code" />
    </el-form-item>
    <el-form-item label="数据个数">
      <el-input-number v-model="form.dataCount" :min="0" controls-position="right" />
    </el-form-item>
    <span v-for="i in form.dataCount">
      <el-form-item :label="'数据 ' + i">
        <el-input v-model="form.data['data' + i]" />
      </el-form-item>
    </span>
    <el-form-item label="帧尾">
      <el-input v-model="form.trailer" />
    </el-form-item>
    <el-form-item>
      <div>
        <el-button type="primary" @click="onSubmit">提交</el-button>
      </div>
      <div>
        <el-button>取消</el-button>
      </div>
    </el-form-item>
  </el-form>

</template>


<style>
.form-all .el-form-item {
  width: 80px;
}

.el-input__wrapper {
  box-shadow: 0;
}
</style>