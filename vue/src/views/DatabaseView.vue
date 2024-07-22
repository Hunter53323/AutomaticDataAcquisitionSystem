<script setup>
import { reactive, ref } from 'vue'
import ViewTitle from '@/components/ViewTitle.vue'
import DBTable from '@/components/database/DBTable.vue'
import { useDBStore } from '@/stores/global'

const db = useDBStore()

db.update()
</script>

<template>
  <ViewTitle viewTitle="Database" />
  <DBTable />
</template>

