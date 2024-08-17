<script lang="ts" setup>
import { ref } from 'vue'
import {
    Document,
    Menu as IconMenu,
    Location,
    Setting,
} from '@element-plus/icons-vue'

</script>


<template>
    <el-menu default-active="/" class="el-menu-vertical-demo" :router="true">
        <el-menu-item index="/">
            <el-icon>
                <location />
            </el-icon>
            <template #title>Dashboard</template>
        </el-menu-item>
        <el-menu-item index="/database">
            <el-icon>
                <icon-menu />
            </el-icon>
            <template #title>Database</template>
        </el-menu-item>
        <el-menu-item index="/settings">
            <el-icon>
                <setting />
            </el-icon>
            <template #title>Settings</template>
        </el-menu-item>
    </el-menu>
</template>


<style>
.el-menu-vertical-demo:not(.el-menu--collapse) {
    width: 150px;
    height: 85vh;
}
</style>