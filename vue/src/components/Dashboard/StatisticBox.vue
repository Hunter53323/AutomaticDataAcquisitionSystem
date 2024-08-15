<script lang="ts" setup>
import { k } from 'vite/dist/node/types.d-aGj9QkWt';
import { computed } from 'vue'

const props = defineProps(['contentObj', 'count'])
const contentLength = computed(() => Object.keys(props.contentObj).length)
const rowCount = computed(() => Math.ceil(contentLength.value / props.count))
const cowSpan = computed(() => 24 / props.count)

const getUnit = (key) => {
  if (key.includes('转速')) {
    return 'rpm'
  } else if (key.includes('电流')) {
    return 'A'
  } else if (key.includes('电压')) {
    return 'V'
  } else if (key.includes('功率')) {
    return 'W'
  } else if (key.includes('温度')) {
    return '°C'
  } else if (key.includes('湿度')) {
    return '%'
  } else {
    return ''
  }
}

</script>

<template>
  <el-row v-for="row in rowCount">
    <el-col v-for="(value, key, index) in props.contentObj" :span="cowSpan">
      <el-statistic v-if="index < row * props.count && index >= row * props.count - props.count" :title="key"
        :value="null" group-separator=" ">
        <template #suffix>
          {{ getUnit(key) }}
        </template>
        <template #prefix>
          <span>{{ value }}</span>
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


.el-statistic :deep .el-statistic__head {
  font-size: 14px!important;
}

.el-statistic :deep() .el-statistic__content {
  font-size: 16px!important;
}
</style>