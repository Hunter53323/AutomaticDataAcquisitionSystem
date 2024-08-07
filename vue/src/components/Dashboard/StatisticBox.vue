<script lang="ts" setup>
import { computed } from 'vue'

const props = defineProps(['contentObj', 'count'])
const contentLength = computed(() => Object.keys(props.contentObj).length)
const rowCount = computed(() => Math.ceil(contentLength.value / props.count))
const cowSpan = computed(() => 24 / props.count)
</script>

<template>
  <el-row v-for="row in rowCount">
    <el-col v-for="(value, key, index) in props.contentObj" :span="cowSpan">
      <el-statistic v-if="index < row * props.count && index >= row * props.count - props.count" :title="key"
        :value="value" group-separator=" " :precision="2" />
    </el-col>
  </el-row>
</template>


<style scoped>
.el-col {
  text-align: center;
}



.el-statistic {
  --el-statistic-title-font-size: --el-font-size-small;
}
</style>