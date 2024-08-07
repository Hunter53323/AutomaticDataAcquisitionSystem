import { defineStore } from 'pinia'

export const useGlobalStore = defineStore('global', {
    state: () => {
        return {
            url: 'http://127.0.0.1:5000'
        }
    }
})

export const useDBStore = defineStore('database', {
    state: () => ({
        columns: [],
        columnsToFill: [],
        colunmsShowSelected: [],
        totalCount: 0,
        pageSize: 5,
        currentPage: 1
    }),
    actions: {
        updateMeta() {
            fetch(useGlobalStore().url + "/db/data/meta", {
                method: 'GET'
            })
                .then(response => response.json())
                .then(data => {
                    this.columns = data.columns
                    this.columnsToFill = data.columns_to_fill
                    this.colunmsShowSelected = data.columns
                    this.totalCount = data.total_count
                })
        },
    }
})

export const useDashboardStore = defineStore('dashboard', {
    state: () => ({
        collectCount: 0,
        collectCountNow: 0,
        isConnected: false,
        isDeviceRunning: false,
        dataList: [],
        dataShowSelected:[]
    }),
    actions: {
        updateDataList() {
            fetch(useGlobalStore().url + "/control/datatranslate", {
                method: 'GET'
            })
                .then(response => response.json())
                .then(data => {
                    this.dataList = Object.keys(data)
                    console.log(this.dataList)
                    this.dataShowSelected = Object.keys(data)
                    console.log(this.dataShowSelected)
                })
        }
    }
})