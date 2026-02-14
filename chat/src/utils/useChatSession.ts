import { defineStore } from "pinia";
import type { User } from '@/utils/useUserStore'
import { useUserStore } from "@/utils/useUserStore";
import { useRouter } from 'vue-router'
import { baseUrl } from "./useRouter.vue";

const router = useRouter()
type Message = {
    time: string,
    fromUser: string
    id: number
    content: string
    type: string
}
type Session = {
    id: string | undefined
    isRead: boolean
    msgNum: number
    contents: Message[]
    members: string[]
}
type SessionStatus = {
    currentSession: string | null
    lastSession: string | null
}
export const useChatSession = defineStore('chatSession', () => {
    const userStore = useUserStore()
    const user = userStore.user
    const router = useRouter()
    let sessionId = router.currentRoute.value.params.id
    if (Array.isArray(sessionId)) {
        sessionId = sessionId[0]
        throw Error('chatSession - arraySession')
    }

    const sessionStatus: SessionStatus = {
        currentSession: null,
        lastSession: null
    }



    async function checkDB(token: string, timeout: number = 5000, successFunction: Function | null = null, failureFunction: Function | null = null): Promise<DB> {
        if (token) {
            const controller = new AbortController()
            let status = false
            let result = null
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
                    result = data
                }

            }
            catch (err) {
                status = false
                throw new Error('checkDB - failedToFetchHttp')
            }
            finally {
                clearTimeout(abort)
            }
            if (status) {
                try {
                    if (successFunction) successFunction()
                    return result
                }
                catch (err) {
                    throw new Error('checkDB - successFunctionError')
                }
            } else {
                try {
                    if (failureFunction) failureFunction()
                    return null
                }
                catch (err) {
                    throw new Error('checkDB - failureFunctionError')
                }
            }
        }
        return null
    }

    type DB = {
        username: string
        sessions: Session[]
    } | null

    const db: DB = null


    async function refreshDB(db: DB = null) {
        console.log('refreshDB')
        db = await checkDB(user.token)
    }

    async function selectSession(name: string, _router: any = router) {
        const isVaild = userStore.verify_token(user.token)
        if (!isVaild) {
            user.status.logined = false
            user.token = ''
            if (_router) {
                _router.push('/login')
            }
            return
        }
        const fromId = user.username
        console.log(`Selecting session with ${name}, fromId: ${fromId}`)
        const toId = name
        try {
            const result_session = await _getSession(user.token, fromId, toId) || null
            sessionStatus.lastSession = sessionStatus.currentSession
            sessionStatus.currentSession = result_session?.id || null

            if (_router) {
                _router.push(`/chat/${name}`)
            }

            return result_session
        }
        catch (err) {
            alert(`会话获取失败，可能网络异常或服务器关闭，亦或者会话对象已经不存在以及你瞎改了url，请刷新，错误信息：${err}`)
            if (_router) {
                _router.push('/chat')
            }
        }
    }

    function initialize() {
        let id = sessionId
        if (Array.isArray(id)) {
            id = id[0]
        }
        sessionStatus.currentSession = null
        sessionStatus.lastSession = null
    }
    initialize() // 初始化

    async function _getAllUsers(token: string, timeout: number = 5000, successFunction: Function | null = null, failureFunction: Function | null = null): Promise<string[] | null> {
        if (token) {
            const controller = new AbortController()
            let status = false
            let result = null
            const abort = setTimeout(() => {
                controller.abort()
            }, timeout)
            try {
                const response = await fetch(`${baseUrl}/users`, {
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
                    result = data
                }

            }
            catch (err) {
                status = false
                console.log(`_getAllUsers - ${err}`)
                throw new Error('_getAllUsers - failedToFetchHttp')
            }
            finally {
                clearTimeout(abort)
            }
            if (status) {
                try {
                    if (successFunction) successFunction()
                    return result
                }
                catch {
                    throw new Error('verifyToken - successFunctionError')
                }

            } else {
                try {
                    if (failureFunction) failureFunction()
                }
                catch (err) {
                    throw new Error('verifyToken - failureFunctionError')
                }
                throw new Error('getAllUsers - failedToFetch')
            }
        }
        throw new Error('getAllUsers - noToken')
    }

    async function _getSession(token: string, checkFrom: string, checkedFrom: string, timeout: number = 5000, successFunction: Function | null = null, failureFunction: Function | null = null): Promise<Session | null> {
        if (token) {
            const controller = new AbortController()
            let status = false
            let result = null
            const abort = setTimeout(() => {
                controller.abort()
            }, timeout)
            try {
                const response = await fetch(`${baseUrl}/get_session`, {
                    'method': 'POST',
                    'headers': {
                        'Content-Type': 'application/json',
                        'Authorization': `Bearer ${token}`
                    },
                    'body': JSON.stringify({
                        'checkFrom': checkFrom,
                        'checkedFrom': checkedFrom
                    }),
                    'signal': controller.signal
                })
                if (response.ok) {
                    const data = await response.json()
                    status = true
                    result = data
                }

            }
            catch (err) {
                status = false
                console.log(`_getSession - ${err}`)
                throw new Error('_getSession - failedToFetchHttp')
            }
            finally {
                clearTimeout(abort)
            }
            if (status) {
                try {
                    if (successFunction) successFunction()
                    return result
                }
                catch {
                    throw new Error('_getSession - successFunctionError')
                }

            } else {
                try {
                    if (failureFunction) failureFunction()
                }
                catch (err) {
                    throw new Error('_getSession - failureFunctionError')
                }
                throw new Error('_getSession - failedToFetch')
            }
        }
        throw new Error('_getSession - noToken')
    }

    async function getAllUsers(token: string): Promise<string[]> {
        const users = await _getAllUsers(token) || []
        return users
    }

    async function sendSessionToDB(session: Session, timeout: number = 5000) {
        const controller = new AbortController()
        const abort = setTimeout(() => {
            controller.abort()
        }, timeout)
        try {
            const response = await fetch(`${baseUrl}/update_session`, {
                'method': 'POST',
                'headers': {
                    'Content-Type': 'application/json',
                },
                'body': JSON.stringify({
                    'session': session
                }),
                'signal': controller.signal
            })
            if (response.ok) {
                return true
            }
            else {
                throw new Error('sendSessionToDB - failedToFetch')
            }
        }
        catch (err) {
            console.log(`sendSessionToDB - ${err}`)
            throw new Error('sendSessionToDB - failedToFetchHttp')
        }
    }
    


    return {
        sessionStatus,
        selectSession,
        initialize,
        getAllUsers,
        refreshDB,
        sendSessionToDB,
        db,
        _getSession
    }
})

export type { Session, Message }

