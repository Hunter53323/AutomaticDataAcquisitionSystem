<script setup lang="ts">
import { computed, nextTick, reactive, ref, watch } from 'vue'
import { Edit } from '@element-plus/icons-vue'

const props = defineProps(['refList', 'selectedList', 'size'])

const selectedList = ref(props.selectedList)

watch(() => props.selectedList, (val) => {
  selectedList.value = val
})
</script>

<template>
  <el-checkbox-group v-model="selectedList" :size="props.size"
    @change="$emit('selectedChange', props.refList.filter((item) => selectedList.includes(item)))">
    <el-checkbox-button v-for="col in props.refList" :key="col" :value="col" class="check-button">
      {{ col }}
    </el-checkbox-button>
  </el-checkbox-group>
</template>

<style scoped>
.check-button{
  margin: 5px 0;
}
</style>