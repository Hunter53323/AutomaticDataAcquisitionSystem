<script setup>
import { reactive, ref, onMounted } from 'vue'
import ViewTitle from '@/components/ViewTitle.vue'
import DBTable from '@/components/database/DBTable.vue'
</script>

<template>
  <ViewTitle viewTitle="Database" />
  <DBTable />
</template>

