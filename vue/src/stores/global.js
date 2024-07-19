import { defineStore } from 'pinia'

export const useGlobalStore = defineStore('global', {
  state: () => {
    return { url: 'http://127.0.0.1:5000' }
  }
})

export const useDBStore = defineStore('db', {
    state:()=>{
        return {}
    }
})