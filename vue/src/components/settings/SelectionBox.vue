<script setup lang="ts">
import { computed, nextTick, reactive, ref, watch } from 'vue'
import { Edit } from '@element-plus/icons-vue'

const props = defineProps(['refList', 'selectedList'])

const selectedList = ref(props.selectedList)

watch(() => props.selectedList, (val) => {
  selectedList.value = val
})
</script>

<template>
  <el-checkbox-group v-model="selectedList"
    @change="$emit('selectedChange', props.refList.filter((item) => selectedList.includes(item)))">
    <el-checkbox-button v-for="col in props.refList" :key="col" :value="col">
      {{ col }}
    </el-checkbox-button>
  </el-checkbox-group>
</template>