<script setup lang="js">
import { ref, onMounted, reactive, watch, computed } from 'vue'
import SelectionBox from '@/components/settings/SelectionBox.vue';
import { useDBStore } from '@/stores/global';

const db = useDBStore()
const activeNames = ref(['1'])



</script>

<template>
  <el-collapse v-model="activeNames">
    <el-collapse-item title="数据库显示" name="1">
      <SelectionBox class="selector" :ref-list="db.columns" :selected-list="db.colunmsShowSelected"
        @selectedChange="(selectedList) => db.colunmsShowSelected = selectedList" />
    </el-collapse-item>
    <el-collapse-item title="数据库存储配置" name="2">
      
    </el-collapse-item>
  </el-collapse>
</template>

<style scoped>
.selector {
  margin: 10px;
}
</style>