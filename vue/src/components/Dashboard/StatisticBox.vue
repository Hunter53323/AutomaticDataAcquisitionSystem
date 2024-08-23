<script lang="ts" setup>
import { computed } from 'vue'
import { useGlobalStore } from '@/stores/global';

const global = useGlobalStore()
const props = defineProps(['contentObj', 'count'])
const contentLength = computed(() => Object.keys(props.contentObj).length)
const rowCount = computed(() => Math.ceil(contentLength.value / props.count))
const cowSpan = computed(() => 24 / props.count)


const fommatValue = (value) => {
  if (typeof value === 'string') {
    return value
  } else if (typeof value === 'number') {
    return value.toFixed(2)
  }
}

</script>

<template>
  <el-row v-for="row in rowCount">
    <el-col v-for="(value, key, index) in props.contentObj" :span="cowSpan">
      <el-statistic v-if="index < row * props.count && index >= row * props.count - props.count" :title="key"
        :value="null" group-separator=" ">
        <template #suffix>
          {{ global.getUnit(key) }}
        </template>
        <template #prefix>
          <span>{{ fommatValue(value) }}</span>
        </template>
      </el-statistic>
    </el-col>
  </el-row>
</template>


<style scoped>
.el-col {
  text-align: center;
}

.el-row {
  margin: 10px 0;
}


.el-statistic :deep(.el-statistic__head) {
  font-size: 14px !important;
}

.el-statistic :deep(.el-statistic__content) {
  font-size: 14px !important;
}
</style>