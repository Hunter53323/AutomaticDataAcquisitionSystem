<script setup lang="ts">
import { ref, onMounted, reactive, watch } from 'vue'
import SelectionBox from '@/components/settings/SelectionBox.vue'
import { useDashboardStore } from '@/stores/global';

const dashboard = useDashboardStore()
const activeNames = ref([])

</script>

<template>
  <el-collapse v-model="activeNames">
    <el-collapse-item title="被测设备" name="1">
      <SelectionBox class="selector" :refList="dashboard.dataList['FanDriver']"
        :selectedList="dashboard.dataShowSelected['FanDriver']"
        @selectedChange="(selectedList) => dashboard.dataShowSelected['FanDriver'] = selectedList" />
    </el-collapse-item>
    <el-collapse-item title="测试设备" name="2">
      <SelectionBox class="selector" :refList="dashboard.dataList['TestDevice']"
        :selectedList="dashboard.dataShowSelected['TestDevice']"
        @selectedChange="(selectedList) => dashboard.dataShowSelected['TestDevice'] = selectedList" />
    </el-collapse-item>
    <el-collapse-item title="参数" name="3">
      <SelectionBox class="selector" :refList="dashboard.paraList" :selectedList="dashboard.paraShowSelected"
        @selectedChange="(selectedList) => dashboard.paraShowSelected = selectedList" />
    </el-collapse-item>
  </el-collapse>
</template>

<style>
.selector {
  margin: 10px;
}

.el-collapse-item__content {
  padding: 0;
}

.el-collapse-item__wrap{
  margin: 0;
}
</style>