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
        isFanConnected: false,
        isTestConnected: false,
        isFanRunning: false,
        isTestRunning: false,
        isFanBreakDown: false,
        isTestBreakDown: false,
        isAutoCollecting: false,
        dataList: {},
        dataShowSelected: {},
        paraList: [],
        paraShowSelected: [],
        
    }),
    actions: {
        initList() {
            fetch(useGlobalStore().url + "/control/data", {
                method: 'GET'
            })
                .then(response => response.json())
                .then(data => {
                    // console.log(data)
                    this.dataList = Object.assign({}, data)
                    this.dataShowSelected = Object.assign({}, this.dataList)
                })
            fetch(useGlobalStore().url + "/control/parameters", {
                method: 'GET'
            })
                .then(response => response.json())
                .then(data => {
                    this.paraList = [...data['FanDriver'],...data['TestDevice']]
                    this.paraShowSelected = this.paraList.slice(0)
                })
        },
        initDeviceState() {
            fetch(useGlobalStore().url + '/control/state', {
                method: 'GET',
            })
                .then((response) => response.json())
                .then((data) => {
                    this.isFanConnected = data.FanDriver.connected
                    this.isFanRunning = data.FanDriver.running
                    this.isFanBreakDown = data.FanDriver.breakdown
                    this.isTestConnected = data.TestDevice.connected
                    this.isTestRunning = data.TestDevice.running
                    this.isTestBreakDown = data.TestDevice.breakdown
                })
                .catch(error => {

                })
        }
    }
})
export const useSettingsStore = defineStore('settings', {
    state: () => ({
        staffInfo: {},
    }),
    actions: {
        initSettings() {
            fetch(useGlobalStore().url + "/control/config", {
                method: 'GET'
            })
                .then(response => response.json())
                .then(data => {
                    this.staffInfo = data
                })
        }
    }