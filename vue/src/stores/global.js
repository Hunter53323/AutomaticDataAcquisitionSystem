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
        columnsToFill: []
    }),
    actions: {
        update() {
            fetch(useGlobalStore().url + "/db/data/columns", {
                method: 'GET'
            })
                .then(response => response.json())
                .then(data => {
                    this.columns = data.columns
                    this.columnsToFill = data.columns_to_fill
                })
        }
    }
})