import { column } from 'element-plus/es/components/table-v2/src/common'
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
        update() {
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
        changePageSize(pageSize) {
            this.pageSize = pageSize
        },
        updateTotalCount(count) {
            this.totalCount = count
        },
        changeCurrentPage(page) {
            this.currentPage = page
        }
    }
})