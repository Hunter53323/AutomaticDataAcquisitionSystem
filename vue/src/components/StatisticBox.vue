<script lang="ts" setup>
import { ref, reactive, computed } from 'vue'
import { useTransition } from '@vueuse/core'
import { ChatLineRound, Male } from '@element-plus/icons-vue'

const source = ref(0)
const outputValue = useTransition(source, {
  duration: 1500,
})
source.value = 172000

const content = reactive({
  name1: 234,
  name2: 12,
  name3: 9999,
  q23123: 123414,
  ada: 42516136534,
  qqqqq: 12314234123.12312
})
const contentLength = computed(() => Object.keys(content).length)
</script>

<template>
  <div class="statisticBox">
    <el-row v-for="row in Math.ceil(contentLength / 4)">
      <el-col v-for="(value, key, index) in content" :span="6">
        <el-statistic v-if="index < row * 4 && index >= row * 4 - 4" :title="key" :value="value" group-separator=" " :precision=2 />
      </el-col>
    </el-row>
  </div>
</template>


<style scoped>
.el-col {
  text-align: center;
}

.el-row{
  margin:  20px 50px 20px 50px;
}
.el-statistic {
  --el-statistic-title-font-size: --el-font-size-small;
}

</style>