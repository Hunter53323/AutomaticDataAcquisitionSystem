<script lang="ts" setup>
import { ref } from 'vue'

const url = 'http://127.0.0.1:5000'
const props = defineProps(['selectList'])

const handleDBDelete = (id) => {
  fetch(url + "/db/data", {
    method: 'DELETE',
    body: JSON.stringify({ ids_input: id }),
    headers: {
      'Content-Type': 'application/json'
    }
  }).then(response => response.json())
    .then(data => {
    })
}

</script>
<template>
  <el-button type="primary" @click="handleDBDelete(props.selectList)">DELETE</el-button>
</template>