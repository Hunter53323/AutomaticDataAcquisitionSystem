<script setup lang="ts">
import { ref } from 'vue'
import { useDBStore } from '@/stores/global';
import ShowSelection from '@/components/ShowSelection.vue'

const db = useDBStore()

const handlePageSizeChange = () => {
  db.currentPage = 1
  db.dbDataUpdate()
}

</script>

<template>

  <div class="demo-pagination-block">
    <el-pagination v-model:current-page="db.currentPage" v-model:page-size="db.pageSize" :page-sizes="[10, 20, 30, 50]"
      size="default" background layout="slot, total, sizes, prev, pager, next, jumper" :total="db.totalCount"
      @size-change="handlePageSizeChange" @current-change="db.dbDataUpdate()">
      <template #default>
        <ShowSelection :ref-list="db.columns" :selected-list="db.colunmsShowSelected"
          @selected-change="(selectedList) => db.colunmsShowSelected = selectedList" />
      </template>
    </el-pagination>

  </div>

</template>

<style scoped>
.el-pagination {
  width: 100vb;
  text-align: center;
  margin: auto;
  margin-top: 20px;
}
</style>