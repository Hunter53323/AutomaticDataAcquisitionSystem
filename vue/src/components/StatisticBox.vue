<script lang="ts" setup>
import { computed } from 'vue'

const props = defineProps(['contentObj', 'title'])
const contentLength = computed(() => Object.keys(props.contentObj).length)
</script>

<template>
  <div class="statisticBox">
    <div class="statisticTitle">
      {{ props.title }}
    </div>
    <el-row v-for="row in Math.ceil(contentLength / 6)">
      <el-col v-for="(value, key, index) in props.contentObj" :span="4">
        <el-statistic v-if="index < row * 6 && index >= row * 6 - 6" :title="key" :value="value" group-separator=" "
          :precision="2" />
      </el-col>
    </el-row>
  </div>
</template>


<style scoped>
.el-col {
  text-align: center;
}

.el-row {
  margin: 20px 20px 20px 20px;
}

.el-statistic {
  --el-statistic-title-font-size: --el-font-size-small;
}

.statisticTitle {
  text-align: left;
  font-size: 20px;
  margin: 0 0 0 20px;
}
</style>