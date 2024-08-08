<script setup>
import { computed, nextTick, reactive, ref, watch } from 'vue'
import { Edit } from '@element-plus/icons-vue'

const props = defineProps(['refList', 'selectedList'])

const selectedList = ref(props.selectedList)
const width = ref(0)

watch(() => props.selectedList, (val) => {
  selectedList.value = val
})

function updateWidth() {
  try {
    const element = this.$refs.checkboxGroup;
    const rect = element.getBoundingClientRect();
    if (width.value !== rect.width) {
      return
    }
    width.value = rect.width;
  }
  catch (err) {

  }
}

</script>

<template>
  <el-popover popper-class="dataPopover" placement="top" trigger="click" :width="width" title="选择你要显示的数据"
    @show="updateWidth">
    <div ref="checkboxGroup">
      <el-checkbox-group v-model="selectedList" size="small" @change="$emit('selectedChange',selectedList)">
        <el-checkbox-button v-for="col in props.refList" :key="col" :value="col">
          {{ col }}
        </el-checkbox-button>
      </el-checkbox-group>
    </div>
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