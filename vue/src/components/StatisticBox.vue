<script lang="ts" setup>
import { ref, reactive, computed } from 'vue'

const props = defineProps(['contentObj'])
const contentLength = computed(() => Object.keys(props.contentObj).length)
</script>

<template>
  <div class="statisticBox">
    <el-row v-for="row in Math.ceil(contentLength / 4)">
      <el-col v-for="(value, key, index) in props.contentObj" :span="6">
        <el-statistic v-if="index < row * 4 && index >= row * 4 - 4" :title="key" :value="value" group-separator=" "
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
  margin: 20px 50px 20px 50px;
}

.el-statistic {
  --el-statistic-title-font-size: --el-font-size-small;
}
</style>