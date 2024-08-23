<script setup lang="ts">
import { reactive, ref } from 'vue'
import { useSettingsStore, useGlobalStore, useDashboardStore } from '@/stores/global';
import { ElMessage } from 'element-plus';

const settings = useSettingsStore()
const dashboard = useDashboardStore()
const global = useGlobalStore()
const form = reactive({
  formula: '',
  name: '',
})

const handleClick = (item) => {
  form.formula += item
}

const uploadUserColumn = () => {
  const formdata = new FormData();
  formdata.append("name", form.name);
  formdata.append("formula", form.formula);
  fetch(global.url + '/control/custom_column', {
    method: 'POST',
    body: formdata,
  })
    .then(data => data.json())
    .then(data => {
      if (data.status != true) {
        throw new Error()
      }
      ElMessage({
        message: '自定义列添加成功',
        type: 'success'
      })
      settings.updateDefined()
    })
    .catch(err => {
      ElMessage.error('自定义列添加失败')
    })
}

const handleTagClose = (item) =>{
  const formdata = new FormData();
  formdata.append("name", item);
  fetch(global.url + '/control/custom_column', {
    method: 'DELETE',
    body: formdata,
  })
    .then(data => data.json())
    .then(data => {
      if (data.status != true) {
        throw new Error()
      }
      ElMessage({
        message: '自定义列删除成功',
        type: 'success'
      })
      settings.updateDefined()
    })
    .catch(err => {
      ElMessage.error('自定义列删除失败')
    })
}


</script>

<template>
  <div>
    <el-row class="defined-div">
      <el-text class="tip-text">
        已定义列
      </el-text>
      <el-tooltip v-for="(value, key) in settings.definedColumns" effect="light" placement="top">
        <template #content>
          <el-text>
            {{ value }}
          </el-text>
        </template>
        <el-tag closable type="primary" effect="light" size="large" @close="handleTagClose(key)">
          {{ key }}
        </el-tag>
      </el-tooltip>
    </el-row>
    <el-row class="choice" :gutter="20">
      <el-col :span="18">
        <el-text class="tip-text">可选变量</el-text>
        <el-button-group>
          <el-button v-for="item in dashboard.dataList" type="success" @click="handleClick(item)" size="small">
            {{ item }}
          </el-button>
        </el-button-group>
      </el-col>
      <el-col :span="6">
        <el-text class="tip-text">可选算符</el-text>
        <el-button-group>
          <el-button v-for="item in settings.operationChoice" type="success" @click="handleClick(item)" size="small">
            {{ item }}
          </el-button>
        </el-button-group>
      </el-col>
    </el-row>
    <el-row class="formula-input" :gutter="20">
      <el-col :span="4">
        <el-input v-model="form.name" placeholder="输入自定义变量名" clearable></el-input>
      </el-col>
      <el-col :span="1">
        <el-text class="equal-text">=</el-text>
      </el-col>
      <el-col :span="17">
        <el-input v-model="form.formula" placeholder="输入自定义变量计算公式" clearable></el-input>
      </el-col>
      <el-col :span="2">
        <el-button type="success" @click="uploadUserColumn">添加</el-button>
      </el-col>
    </el-row>
  </div>
</template>

<style scoped>
.div {
  margin: 10px;
}

.defined-div {
  height: 32px;
}

.defined-div .el-tag {
  margin: 0px 10px 0 0;
}

.tip-text {
  margin: 0 10px 0 0;
}



.equal-text {
  font-size: 24px;
  font-weight: bolder;
}

.el-row {
  margin: 10px 0;
}

.formula-input .el-col {
  display: flex;
  justify-content: center;
  align-items: center;
}
</style>