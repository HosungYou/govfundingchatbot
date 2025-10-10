'use client'

import { useState, useEffect } from 'react'

interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  timestamp: number
}

interface ChatSession {
  id: string
  title: string
  messages: Message[]
  createdAt: number
  updatedAt: number
}

export default function ChatHistory() {
  const [sessions, setSessions] = useState<ChatSession[]>([])
  const [selectedSession, setSelectedSession] = useState<ChatSession | null>(null)

  useEffect(() => {
    loadSessions()

    // Listen for storage changes to update in real-time
    const handleStorageChange = () => {
      loadSessions()
    }

    window.addEventListener('storage', handleStorageChange)

    // Poll for changes every 2 seconds (in case same-tab updates don't trigger storage event)
    const interval = setInterval(loadSessions, 2000)

    return () => {
      window.removeEventListener('storage', handleStorageChange)
      clearInterval(interval)
    }
  }, [])

  const loadSessions = () => {
    const stored = localStorage.getItem('chat_sessions')
    if (stored) {
      const parsed = JSON.parse(stored)
      setSessions(parsed)
    }
  }

  const deleteSession = (sessionId: string) => {
    const updated = sessions.filter((s) => s.id !== sessionId)
    localStorage.setItem('chat_sessions', JSON.stringify(updated))
    setSessions(updated)
    if (selectedSession?.id === sessionId) {
      setSelectedSession(null)
    }
  }

  const continueSession = (session: ChatSession) => {
    // Trigger the FloatingChat to open with this session
    // For now, we'll just select it to view
    setSelectedSession(selectedSession?.id === session.id ? null : session)
  }

  if (sessions.length === 0) {
    return (
      <div className="bg-white rounded-xl border border-neutral-200 p-12 text-center">
        <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
          <svg className="w-8 h-8 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        </div>
        <h3 className="text-lg font-semibold text-neutral-900 mb-2">No conversations yet</h3>
        <p className="text-neutral-600 mb-4">
          Click the chat button in the bottom right to start asking AI about grants.
        </p>
      </div>
    )
  }

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-neutral-900">AI Chat History</h2>
        <span className="text-sm text-neutral-500">{sessions.length} conversation{sessions.length !== 1 ? 's' : ''}</span>
      </div>

      <div className="space-y-3">
        {sessions.map((session) => (
          <div key={session.id} className="bg-white rounded-xl border border-neutral-200 overflow-hidden">
            <div
              className="p-4 cursor-pointer hover:bg-neutral-50 transition"
              onClick={() => continueSession(session)}
            >
              <div className="flex items-start justify-between mb-2">
                <h3 className="font-semibold text-neutral-900 flex-1 line-clamp-1">
                  {session.title}
                </h3>
                <button
                  onClick={(e) => {
                    e.stopPropagation()
                    deleteSession(session.id)
                  }}
                  className="ml-2 p-1 text-neutral-400 hover:text-red-600 transition"
                  title="Delete conversation"
                >
                  <svg className="w-4 h-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16" />
                  </svg>
                </button>
              </div>

              <div className="flex items-center gap-3 text-xs text-neutral-500">
                <span>{session.messages.length} message{session.messages.length !== 1 ? 's' : ''}</span>
                <span>•</span>
                <span>{new Date(session.updatedAt).toLocaleDateString()}</span>
                <span>•</span>
                <span>{new Date(session.updatedAt).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}</span>
              </div>
            </div>

            {/* Expanded View */}
            {selectedSession?.id === session.id && (
              <div className="border-t border-neutral-200 bg-neutral-50 p-4 max-h-96 overflow-y-auto">
                <div className="space-y-3">
                  {session.messages.map((message) => (
                    <div
                      key={message.id}
                      className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                    >
                      <div
                        className={`max-w-[80%] rounded-lg px-4 py-2 ${
                          message.role === 'user'
                            ? 'bg-primary-500 text-white'
                            : 'bg-white text-neutral-900 border border-neutral-200'
                        }`}
                      >
                        <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                        <p className={`text-xs mt-1 ${message.role === 'user' ? 'text-primary-100' : 'text-neutral-500'}`}>
                          {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                        </p>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    </div>
  )
}
