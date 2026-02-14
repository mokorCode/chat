import { defineStore } from "pinia";
import { ref } from "vue"
import type { Ref } from "vue"
import { baseUrl } from "./useRouter.vue";

type User = {
    username: string,
    status: {
        logined: Ref<boolean>
    }
    token: Ref<string>
}

export const useUserStore = defineStore('user', () => {
    async function me(token: string, timeout: number = 5000, successFunction: Function | null = null, failureFunction: Function | null = null) {
        if (token) {
            const controller = new AbortController()
            let status = false
            let result = ''
            const abort = setTimeout(() => {
                controller.abort()
            }, timeout)
            try {
                const response = await fetch(`${baseUrl}/me`, {
                    'method': 'POST',
                    'headers': {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    'signal': controller.signal
                })
                if (response.ok) {
                    const data = await response.json()
                    status = true
                    result = data.username
                    return result
                }
                
            }
            catch (err) {
                status = false
                throw new Error('me - failedToFetch')
            }
            finally {
                clearTimeout(abort)
            }
            if (status) {
                try {
                    if (successFunction) successFunction
                    return result
                }
                catch {
                    throw ('me - successFunctionError')
                }
            } else {
                try {
                    if (failureFunction) failureFunction
                }
                catch {
                    throw ('me - failureFunctionError')
                }
            }
        }
        return ''
    }
    
    let token = ref(localStorage.getItem('token') ?? '')
    const logined = ref(false)
    let username = ''
    const user: User = {
        username: username,
        status: {
            logined: logined
        },
        token: token
    }
    async function _updateUsername() {
        console.log('_updateUsername: Updating username...')
        user.username = await me(user.token.value)
    }
    _updateUsername()
    
    async function verify_token(token: string, timeout: number = 5000, successFunction: Function | null = null, failureFunction: Function | null = null) {
        if (token) {
            const controller = new AbortController()
            let status = false
            let result = ''
            const abort = setTimeout(() => {
                controller.abort()
            }, timeout)
            try {
                const response = await fetch(`${baseUrl}/token`, {
                    'method': 'POST',
                    'headers': {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    'signal': controller.signal
                })
                if (response.ok) {
                    const data = await response.json()
                    status = true
                    result = data.access_token
                }

            }
            catch (err) {
                status = false
                throw new Error('verifyToken - faildToFetch') // maybe invalid token 
            }
            finally {
                clearTimeout(abort)
            }
            if (status) {
                try {
                    if (successFunction) successFunction
                    return result
                }
                catch {
                    throw ('verifyToken - successFunctionError')
                }
            } else {
                try {
                    if (failureFunction) failureFunction
                }
                catch {
                    throw ('verifyToken - failureFunctionError')
                }
            }
        }
        return ''
    }
    async function initialize() {
        try {
            if (user.token.value) {
                const new_token: string = await verify_token(user.token.value)
                localStorage.setItem('token', new_token)
                user.token.value = new_token
                user.status.logined.value = true
                _updateUsername()
            }
        }
        catch (err: any) {
            console.log(`Error - ${err}`)
        }
    }

    async function tokenLogin(token: string, timeout: number = 5000, successFunction: Function | null = null, failureFunction: Function | null = null) {
        const controller = new AbortController()
        const abort = setTimeout(() => {
            controller.abort()
        }, timeout)
        try {
            const response = await fetch(`${baseUrl}/token`, {
                'method': 'POST',
                'headers': {
                    'Content-Type': 'application/json',
                    'Authorization': `Bearer ${token}`
                },
                'signal': controller.signal
            })
            if (response.ok) {
                const data = await response.json()
                localStorage.setItem('token', data.access_token)
                alert(`
            自动登录成功
            new token: ${data.access_token}
            `)
                try {
                    if (successFunction) successFunction()
                }
                catch {
                    throw Error('autoLogin-functionError')
                }
            }
            else {
                alert(`response: ${response.statusText},
            自动登录失败`)
                try {
                    if (failureFunction) failureFunction()
                }
                catch {
                    throw Error('autoLogin-functionError')
                }
            }
        }
        catch {
            alert('连接超时')
            try {
                if (failureFunction) failureFunction()
            }
            catch {
                throw Error('autoLogin-functionError')
            }

        }
        finally {
            clearTimeout(abort)
        }


    }
    return { token, logined, verify_token, initialize, tokenLogin, user, me }
})

export type { User }