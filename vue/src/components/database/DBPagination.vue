<script setup lang="ts">
import { ref } from 'vue'
import { useDBStore } from '@/stores/global';
import ShowSelection from '@/components/ShowSelection.vue'

const db = useDBStore()
const emit = defineEmits(['pageChange', 'sizeChange'])

</script>

<template>

  <div class="demo-pagination-block">
    <el-pagination v-model:current-page="db.currentPage" v-model:page-size="db.pageSize"
      :page-sizes="[5, 10, 20, 30, 50]" size="default" background layout="slot, total, sizes, prev, pager, next, jumper"
      :total="db.totalCount" @size-change="$emit('sizeChange')" @current-change="$emit('pageChange')">
      <template #default>
        <ShowSelection :ref-list="db.columns" :selected-list="db.colunmsShowSelected"
          @selected-change="(selectedList) => db.colunmsShowSelected = selectedList" />
      </template>
    </el-pagination>

  </div>

</template>

<style>
.el-pagination {
  width: 100vb;
  text-align: center;
  margin: auto;
  margin-top: 20px;
}
</style>