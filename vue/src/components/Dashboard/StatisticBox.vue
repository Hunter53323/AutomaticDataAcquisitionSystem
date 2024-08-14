<script lang="ts" setup>
import { computed } from 'vue'

const props = defineProps(['contentObj', 'count'])
const contentLength = computed(() => Object.keys(props.contentObj).length)
const rowCount = computed(() => Math.ceil(contentLength.value / props.count))
const cowSpan = computed(() => 24 / props.count)

const getUnit = (key) => {
  if ('转速' in key) {
    return 'rpm'
  } else if ('电流' in key) {
    return 'A'
  } else if ('电压' in key) {
    return 'V'
  } else if ('功率' in key) {
    return 'W'
  } else if ('温度' in key) {
    return '°C'
  } else if ('湿度' in key) {
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
        :value="value" group-separator=" " :precision="2">
        <template #suffix>
          {{ getUnit(key) }}
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



.el-statistic {
  --el-statistic-title-font-size: --el-font-size-small;
}
</style>