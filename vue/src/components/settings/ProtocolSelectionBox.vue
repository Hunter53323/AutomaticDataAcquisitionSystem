<script setup lang="js">
import { ref, watch } from 'vue';
import { useSettingsStore } from '@/stores/global'
import { Close } from '@element-plus/icons-vue'

const settings = useSettingsStore();

const model = defineModel()
// const props = defineProps(['driver'])

</script>

<template>
  <!-- <div class="el-message-box__message">请选择要加载的配置</div>
  <el-select v-model="model.value" placeholder="请选择配置" class="el-message-box__input">
    <el-option v-for="item in settings.protocolChoice[props.driver]" :label="item[2]" :value="item[0]" :key="item[0]">
      <template #default>
        <div class="protocol-item">
          <span>{{ item[2] }}</span>
        </div>
      </template>
    </el-option>

  </el-select> -->
  <div class="el-message-box__message">请选择要加载的配置</div>
  <el-select v-model="model.value" placeholder="请选择配置" class="el-message-box__input">
    <el-option v-for="item in settings.protocolChoice" :label="item[2]" :value="item[0]" :key="item[0]">
      <template #default>
        <div class="protocol-item">
          <span>{{ item[2] }}</span>
        </div>
      </template>
    </el-option>

  </el-select>
</template>

<style scoped>
.protocol-item{
  display: flex;
  justify-content: space-between;
  align-items: center;
}

</style>