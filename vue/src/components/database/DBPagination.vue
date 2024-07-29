<script setup lang="ts">
import { ref } from 'vue'
import type { ComponentSize } from 'element-plus'
import { useDBStore } from '@/stores/global';

const db = useDBStore()
const emit = defineEmits(['pageChange', 'sizeChange'])

</script>

<template>

  <div class="demo-pagination-block">
    <el-pagination
      v-model:current-page="db.currentPage"
      v-model:page-size="db.pageSize"
      :page-sizes="[5, 10, 20, 30, 50]"
      size="default"
      background
      layout="total, sizes, prev, pager, next, jumper"
      :total="db.totalCount"
      @size-change="$emit('sizeChange')"
      @current-change="$emit('pageChange')"
    />
  </div>

</template>

<style>
.el-pagination{
  width: 100vb;
  text-align: center;
  margin: auto;
  margin-top: 20px;
}
</style>