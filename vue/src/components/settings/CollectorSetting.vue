<script setup lang="js">
import { ref, watch, reactive } from 'vue';
import { useGlobalStore, useDashboardStore, useSettingsStore } from '@/stores/global';
import { ElMessage } from 'element-plus';

const form = reactive({})
const global = useGlobalStore()
const settings = useSettingsStore()
const activeNames = ref(['1', '2'])
const dashboard = useDashboardStore()

const formSteady = reactive({
  '实际值': '',
  '设定值': '',
})


watch(() => dashboard.paraList, (value) => {
  value.forEach((item) => {
    form[item] = {
      min: 0,
      max: 0,
      step: 0,
    }
  })
}, { deep: true })


watch(() => settings.steadyConf, (value) => {
  formSteady['实际值'] = value['实际值']
  formSteady['设定值'] = value['设定值']
}, { deep: true })


const updatePara = () => {
  activeNames.value.push('2')
  fetch(global.url + '/collect/uploadparameter', {
    body: JSON.stringify({ parameters: form }),
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  })
    .then((response) => response.json())
    .then(data => {
      dashboard.collectCount = data.line_count
      dashboard.updateCollectState()
      ElMessage.success('参数上传成功');
    })
    .catch((error) => {
      ElMessage.error('参数上传失败');
    });
}

const uploadStable = () => {
  fetch(global.url + '/collect/steady_state_determination', {
    body: JSON.stringify({ value: formSteady }),
    method: 'POST',
    headers: {
      'Content-Type': 'application/json'
    }
  })
    .then((response) => response.json())
    .then(data => {
      ElMessage.success('稳态判定参数上传成功');
    })
    .catch((error) => {
      ElMessage.error('稳态判定参数上传失败');
    });
}

</script>

<template>
  <el-collapse v-model="activeNames" class="collapse-son">
    <el-collapse-item title="稳态判定" name="1">
      <el-form label-position="left" label-width="auto">

        <el-row :gutter="20">
          <el-col :span="11">
            <el-form-item label="实际值" style="width: 100%">
              <el-select v-model="formSteady['实际值']">
                <el-option v-for="item in [...dashboard.dataList, ...dashboard.paraList]" :key="item"
                  :label="item" :value="item" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="11">
            <el-form-item label="设定值" style="width: 100%">
              <el-select v-model="formSteady['设定值']">
                <el-option v-for="item in [...dashboard.dataList, ...dashboard.paraList]" :key="item"
                  :label="item" :value="item" />
              </el-select>
            </el-form-item>
          </el-col>
          <el-col :span="2">
            <el-button type="success" @click="uploadStable">提交</el-button>
          </el-col>
        </el-row>
      </el-form>
    </el-collapse-item>
    <el-collapse-item name="2">
      <template #title>
        <div>参数设置</div>

        <span v-show="activeNames.some(item => item === '2')">
          <el-divider direction="vertical" />
          <el-button size="small" type="primary" @click="updatePara()" class="bntProtocol">
            上传参数
          </el-button>
        </span>
      </template>
      <div v-for="(value, key) in form">
        <el-text size="large">{{ key }}</el-text>
        <el-form :model="form[key]" labelPosition="left" labelWidth="auto" inline class="collector-form">
          <el-row :gutter="20">
            <el-col :span="8">
              <el-form-item label="起始值" :key="key" style="width: 100%">
                <el-input-number v-model="form[key].min" :min="0" :controls="false" style="width: 90%" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="结束值" :key="key" style="width: 100%">
                <el-input-number v-model="form[key].max" :min="0" :controls="false" style="width: 90%" />
              </el-form-item>
            </el-col>
            <el-col :span="8">
              <el-form-item label="步长" :key="key" style="width: 100%">
                <el-input-number v-model="form[key].step" :min="0" :controls="false" style="width: 90%" />
              </el-form-item>
            </el-col>
          </el-row>
        </el-form>
      </div>
    </el-collapse-item>
  </el-collapse>
</template>

<style scoped>
.bntProtocol {
  margin: 0;
}

.collector-form .el-form-item {
  margin: 0 10px;
}

.collector-form {
  margin: 0 0 10px 0;
}
</style>