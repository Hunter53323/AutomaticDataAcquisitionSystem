<script setup lang="js">
import { ref, onMounted, reactive, watch, computed } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus';

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

const addItem = () => {
  ElMessageBox.prompt("请输入需要添加的报表信息", {
    showCancelButton: true,
    cancelButtonText: "取消",
    confirmButtonText: "确认"
  })
    .then(val => {
      form.value.input_form[val.value] = ""
    })
    .catch((err) => {
      console.log(err)
      ElMessage.info("报表信息添加取消")
    })

}



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
    <el-form-item label="选择电机参数">
      <el-cascader v-model="form.data_column" placeholder="请选择要记录的数据" :options="options" :props="prop"
        style="width: 100%" clearable />
    </el-form-item>
    <el-form-item v-for="value, key in form.input_form" :label="key">
      <el-input v-model="form.input_form[key]" :placeholder="'请输入' + key" style="width: 100%" clearable />
    </el-form-item>
  </el-form>
  <div class="add-div">
    <el-button type="success" size="small" class="add-bnt" @click="addItem" link>添加信息</el-button>
  </div>
</template>



<style scoped>
.add-div {
  display: flex;
  justify-content: flex-end;
  margin: 10px 0 0 0;
}

.add-bnt {
  margin: 0;
}
</style>