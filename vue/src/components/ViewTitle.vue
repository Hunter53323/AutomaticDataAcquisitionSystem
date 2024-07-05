<script setup>
defineProps(
  {
    viewTitle: {
      required: true
    }
  }
)
</script>

<template>
  <div class="viewTitle">
    {{ viewTitle }}
  </div>
</template>

<style>
.viewTitle {
  width: 100vb;
  margin: auto;
  text-align: center;
  font-size: 40px;
}
</style>