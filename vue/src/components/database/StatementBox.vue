<script setup lang="js">
import { ref, onMounted, reactive, watch, computed } from 'vue'

const form = defineModel()
const props = defineProps(['columns'])
const prop = { multiple: true }

const options = ref([])


props.columns.forEach((item) => {
  options.value.push({
    value: item,
    label: item,
    children: []
  })
})


</script>

<template>
  <el-form labelPosition="left" labelWidth="auto">
    <el-form-item label="导出文件名">
      <el-input v-model="form.filename" placeholder="请输入导出文件名" clearable>
        <template #append>
          .pdf
        </template>
      </el-input>
    </el-form-item>
    <el-form-item label="导出 ID">
      <el-input v-model="form.ids_input" placeholder="请输入导出 ID，如1，2，5-10" clearable></el-input>
    </el-form-item>
    <el-form-item label="选择绘制">
      <el-cascader v-model="form.draw_parameters" placeholder="请选择要绘制的数据" :options="options" :props="prop"
        style="width: 100%" clearable />
    </el-form-item>
    <el-form-item label="选择数据">
      <el-cascader v-model="form.data_column" placeholder="请选择要记录的数据" :options="options" :props="prop"
        style="width: 100%" clearable />
    </el-form-item>
    <el-form-item label="实验员">
      <el-input v-model="form.input_form['实验员姓名']" placeholder="请输入实验员名称" style="width: 100%" clearable />
    </el-form-item>
    <el-form-item label="公司名称">
      <el-input v-model="form.input_form['公司名称']" placeholder="请输入公司名称" clearable />
    </el-form-item>

  </el-form>

</template>