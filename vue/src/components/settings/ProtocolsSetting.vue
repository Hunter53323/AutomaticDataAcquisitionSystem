<script setup lang="ts">
import { ref, onMounted, reactive, watch, computed } from 'vue'

const formShare = reactive({
  header: 0,
  address: 0,
  trailer: 0
})

const formTestRead = reactive({
  code: 0,
  dataCount: 0,
})

const formTestWrite = reactive({
  code: 0,
  dataCount: 0,
})

const formFanRead = reactive({
  code: 0,
  dataCount: 0,
})

const formFanWrite = reactive({
  code: 0,
  dataCount: 0,
})

watch(() => formTestWrite.dataCount, (newVal, oldVal) => {
  for (let i = 1; i <= newVal; i++) {
    if (!formTestWrite['data' + i]) {
      formTestWrite['data' + i] = 0
    }
  }
  for (let i = newVal + 1; i <= oldVal; i++) {
    delete formTestWrite['data' + i]
  }
}, { deep: true })

watch(() => formFanRead.dataCount, (newVal, oldVal) => {
  for (let i = 1; i <= newVal; i++) {
    if (!formFanRead['data' + i]) {
      formFanRead['data' + i] = 0
    }
  }
  for (let i = newVal + 1; i <= oldVal; i++) {
    delete formFanRead['data' + i]
  }
}, { deep: true })

watch(() => formFanWrite.dataCount, (newVal, oldVal) => {
  for (let i = 1; i <= newVal; i++) {
    if (!formFanWrite['data' + i]) {
      formFanWrite['data' + i] = 0
    }
  }
  for (let i = newVal + 1; i <= oldVal; i++) {
    delete formFanWrite['data' + i]
  }
}, { deep: true })


watch(() => formTestRead.dataCount, (newVal, oldVal) => {
  for (let i = 1; i <= newVal; i++) {
    if (!formTestRead['data' + i]) {
      formTestRead['data' + i] = 0
    }
  }
  for (let i = newVal + 1; i <= oldVal; i++) {
    delete formTestRead['data' + i]
  }
}, { deep: true })

const formTestReadLength = computed(() => Object.keys(formTestRead).length + 3)
const formTestWriteLength = computed(() => Object.keys(formTestWrite).length + 3)
const formFanReadLength = computed(() => Object.keys(formFanRead).length + 3)
const formFanWriteLength = computed(() => Object.keys(formFanWrite).length + 3)

const onSubmit = () => {
  console.log(formTestRead)
}
</script>

<template>
  <el-descriptions title="测试设备协议" direction="vertical" :column="formTestReadLength" border>
    <el-descriptions-item label="帧头">
      <el-input class="inputItem" v-model="formShare.header" />
    </el-descriptions-item>
    <el-descriptions-item label="地址">
      <el-input class="inputItem" v-model="formShare.address" />
    </el-descriptions-item>
    <el-descriptions-item label="命令码">
      <el-input class="inputItem" v-model="formTestRead.code" />
    </el-descriptions-item>
    <el-descriptions-item label="数据个数">
      <el-input-number class="inputItem" v-model="formTestRead.dataCount" :min="0" />
    </el-descriptions-item>
    <span v-for="i in formTestRead.dataCount">
      <el-descriptions-item :label="'数据 ' + i">
        <el-input class="inputItem" v-model="formTestRead['data' + i]" />
      </el-descriptions-item>
    </span>
    <el-descriptions-item label="帧尾">
      <el-input class="inputItem" v-model="formShare.trailer" />
    </el-descriptions-item>
  </el-descriptions>

  <el-descriptions title="测试设备写" direction="vertical" :column="formTestWriteLength" border>
    <el-descriptions-item label="帧头">
      <el-input class="inputItem" v-model="formShare.header" />
    </el-descriptions-item>
    <el-descriptions-item label="地址">
      <el-input class="inputItem" v-model="formShare.address" />
    </el-descriptions-item>
    <el-descriptions-item label="命令码">
      <el-input class="inputItem" v-model="formTestWrite.code" />
    </el-descriptions-item>
    <el-descriptions-item label="数据个数">
      <el-input-number class="inputItem" v-model="formTestWrite.dataCount" :min="0" />
    </el-descriptions-item>
    <span v-for="i in formTestWrite.dataCount">
      <el-descriptions-item :label="'数据 ' + i">
        <el-input class="inputItem" v-model="formTestWrite['data' + i]" />
      </el-descriptions-item>
    </span>
    <el-descriptions-item label="帧尾">
      <el-input class="inputItem" v-model="formShare.trailer" />
    </el-descriptions-item>
  </el-descriptions>

  <el-descriptions title="风扇协议" direction="vertical" :column="formFanReadLength" border>
    <el-descriptions-item label="帧头">
      <el-input class="inputItem" v-model="formShare.header" />
    </el-descriptions-item>
    <el-descriptions-item label="地址">
      <el-input class="inputItem" v-model="formShare.address" />
    </el-descriptions-item>
    <el-descriptions-item label="命令码">
      <el-input class="inputItem" v-model="formFanRead.code" />
    </el-descriptions-item>
    <el-descriptions-item label="数据个数">
      <el-input-number class="inputItem" v-model="formFanRead.dataCount" :min="0" />
    </el-descriptions-item>
    <span v-for="i in formFanRead.dataCount">
      <el-descriptions-item :label="'数据 ' + i">
        <el-input class="inputItem" v-model="formFanRead['data' + i]" />
      </el-descriptions-item>
    </span>
    <el-descriptions-item label="帧尾">
      <el-input class="inputItem" v-model="formShare.trailer" />
    </el-descriptions-item>
  </el-descriptions>
  <el-descriptions title="风扇写" direction="vertical" :column="formFanWriteLength" border>
    <el-descriptions-item label="帧头">
      <el-input class="inputItem" v-model="formShare.header" />
    </el-descriptions-item>
    <el-descriptions-item label="地址">
      <el-input class="inputItem" v-model="formShare.address" />
    </el-descriptions-item>
    <el-descriptions-item label="命令码">
      <el-input class="inputItem" v-model="formFanWrite.code" />
    </el-descriptions-item>
    <el-descriptions-item label="数据个数">
      <el-input-number class="inputItem" v-model="formFanWrite.dataCount" :min="0" />
    </el-descriptions-item>
    <span v-for="i in formFanWrite.dataCount">
      <el-descriptions-item :label="'数据 ' + i">
        <el-input class="inputItem" v-model="formFanWrite['data' + i]" />
      </el-descriptions-item>
    </span>
    <el-descriptions-item label="帧尾">
      <el-input class="inputItem" v-model="formShare.trailer" />
    </el-descriptions-item>
  </el-descriptions>
</template>


<style>
.el-input-number {
  width: 200px;
}
.inputItem .el-input__wrapper {
  box-shadow: none;
}

.inputItem .el-input-number__decrease {
  background-color: transparent;
}

.inputItem .el-input-number__increase {
  background-color: transparent;
}

.el-descriptions__content {
  padding: 0px !important;
}

.el-descriptions__title {
  font-weight: normal;
  font-size: 16px;
}
</style>