import { defineStore } from 'pinia'

export const useGlobalStore = defineStore('global', {
    state: () => {
        return {
            url: 'http://127.0.0.1:5000'
        }
    }
})

export const useDBStore = defineStore('db', {
    state: () => ({
        columns: [],
        columnsToFill: [],
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
                    this.totalCount = data.total_count
                })
        },
    }
})

export const useDashboardStore = defineStore('db', {
    state: () => ({
        collectCount: 0,
        collectCountNow: 0,
        isConnected: false,
        isFanRunning: false
    }),
})