<script setup lang="js">
import { ref, reactive } from 'vue';

const props = defineProps(['driver'])

const optionsType = reactive({
  FanDriver: ['int16', 'int8'],
  TestDevice: ['float']
})
const form = defineModel()
const changeSize = (value) => {
  if (props.driver == "FanDriver") {
    if (value == "int16") {
      form.value.size = 2
    } else {
      form.value.size = 1
    }
  } else {
    form.value.size = 4
  }
}
</script>

<template>
  <el-form labelPosition="left" labelWidth="auto">
    <el-form-item label="数据名称" required>
      <el-input v-model="form.name" placeholder="请输入数据名称"></el-input>
    </el-form-item>
    <el-form-item label="计算公式" required>
      <el-input v-model="form.formula" placeholder="请输入计算公式"></el-input>
    </el-form-item>
    <!-- <el-form-item label="反解公式" required>
      <el-input v-model="form.inv_formula" placeholder="请选择反解公式" multiple></el-input>
    </el-form-item> -->
    <!-- <el-form-item label="数据序号" required>
      <el-input v-model="form.index" placeholder="请输入数据序号"></el-input>
    </el-form-item> -->
    <!-- <el-form-item label="数据大小" required>
      <el-select v-model="form.size" placeholder="请选择数据大小">
        <el-option v-for="item in optionsSize" :key="item" :label="item" :value="item" />
      </el-select>
    </el-form-item> -->
    <el-form-item label="数据类型" required>
      <el-select v-model="form.type" placeholder="请选择数据类型" @change="changeSize">
        <el-option v-for="item in optionsType[props.driver]" :key="item" :label="item" :value="item" />
      </el-select>
    </el-form-item>
  </el-form>

</template>
