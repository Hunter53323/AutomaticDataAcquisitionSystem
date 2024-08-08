<script setup>
import { reactive, ref, defineProps } from 'vue'
import { ElDrawer, ElMessageBox } from 'element-plus'
import { useDashboardStore } from '@/stores/global'
import { Edit } from '@element-plus/icons-vue'

const props = defineProps(['device'])

const dashboard = useDashboardStore()

const dataShowSelected = ref([])
const visible = ref(false)


</script>

<template>
  <el-popover popper-class="dataPopover" placement="top" trigger="click" :width="400" title="选择你要显示的数据">
    <el-checkbox-group v-model="dashboard.dataShowSelected[props.device]" size="small">
      <el-checkbox-button v-for="col in dashboard.dataList[props.device]" :key="col" :value="col">
        {{ col }}
      </el-checkbox-button>
    </el-checkbox-group>
    <template #reference>
      <el-button :icon="Edit" link />
    </template>
  </el-popover>

</template>

<style>
.el-button {
  margin: 0 10px 0 0;
}


.dataPopover .el-checkbox-group .el-checkbox-button {
  margin: 5px 0;
}

.dataPopover .el-button {
  margin: 0 0 0 0;
}
</style>