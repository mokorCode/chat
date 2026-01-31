import { defineStore } from "pinia";

export const useUserStore = defineStore('user', () => {
    const token = localStorage.getItem('token')

    return { token }
})