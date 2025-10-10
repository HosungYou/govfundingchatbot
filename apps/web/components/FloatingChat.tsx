'use client'

import { useState, useEffect, useRef } from 'react'

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

export default function FloatingChat() {
  const [isOpen, setIsOpen] = useState(false)
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [currentSessionId, setCurrentSessionId] = useState<string>('')
  const messagesEndRef = useRef<HTMLDivElement>(null)

  // Load or create session on mount
  useEffect(() => {
    const sessions = getSessions()
    if (sessions.length > 0) {
      // Load most recent session
      const latestSession = sessions[0]
      setCurrentSessionId(latestSession.id)
      setMessages(latestSession.messages)
    } else {
      // Create new session
      const newSessionId = createNewSession()
      setCurrentSessionId(newSessionId)
    }
  }, [])

  // Auto-scroll to bottom
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }, [messages])

  // Save messages to localStorage whenever they change
  useEffect(() => {
    if (currentSessionId && messages.length > 0) {
      saveSession(currentSessionId, messages)
    }
  }, [messages, currentSessionId])

  const getSessions = (): ChatSession[] => {
    if (typeof window === 'undefined') return []
    const stored = localStorage.getItem('chat_sessions')
    return stored ? JSON.parse(stored) : []
  }

  const saveSession = (sessionId: string, sessionMessages: Message[]) => {
    const sessions = getSessions()
    const sessionIndex = sessions.findIndex((s) => s.id === sessionId)

    const updatedSession: ChatSession = {
      id: sessionId,
      title: sessionMessages[0]?.content.slice(0, 50) || 'New Conversation',
      messages: sessionMessages,
      createdAt: sessionIndex >= 0 ? sessions[sessionIndex].createdAt : Date.now(),
      updatedAt: Date.now(),
    }

    if (sessionIndex >= 0) {
      sessions[sessionIndex] = updatedSession
    } else {
      sessions.unshift(updatedSession)
    }

    // Keep only last 10 sessions
    const trimmedSessions = sessions.slice(0, 10)
    localStorage.setItem('chat_sessions', JSON.stringify(trimmedSessions))
  }

  const createNewSession = (): string => {
    const newSessionId = `session_${Date.now()}`
    const newSession: ChatSession = {
      id: newSessionId,
      title: 'New Conversation',
      messages: [],
      createdAt: Date.now(),
      updatedAt: Date.now(),
    }

    const sessions = getSessions()
    sessions.unshift(newSession)
    localStorage.setItem('chat_sessions', JSON.stringify(sessions.slice(0, 10)))

    return newSessionId
  }

  const handleNewChat = () => {
    const newSessionId = createNewSession()
    setCurrentSessionId(newSessionId)
    setMessages([])
  }

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()
    if (!input.trim() || isLoading) return

    const userMessage: Message = {
      id: `msg_${Date.now()}`,
      role: 'user',
      content: input.trim(),
      timestamp: Date.now(),
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          messages: [...messages, userMessage].map((m) => ({
            role: m.role,
            content: m.content,
          })),
        }),
      })

      if (!response.ok) throw new Error('Failed to get response')

      const reader = response.body?.getReader()
      const decoder = new TextDecoder()
      let assistantContent = ''

      const assistantMessage: Message = {
        id: `msg_${Date.now() + 1}`,
        role: 'assistant',
        content: '',
        timestamp: Date.now(),
      }

      setMessages((prev) => [...prev, assistantMessage])

      while (reader) {
        const { done, value } = await reader.read()
        if (done) break

        const chunk = decoder.decode(value)
        assistantContent += chunk

        setMessages((prev) => {
          const updated = [...prev]
          updated[updated.length - 1].content = assistantContent
          return updated
        })
      }
    } catch (error) {
      console.error('Chat error:', error)
      const errorMessage: Message = {
        id: `msg_${Date.now() + 1}`,
        role: 'assistant',
        content: 'Sorry, I encountered an error. Please try again.',
        timestamp: Date.now(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <>
      {/* Floating Button */}
      <button
        onClick={() => setIsOpen(!isOpen)}
        className="fixed bottom-6 right-6 z-50 w-14 h-14 bg-gradient-to-br from-primary-500 to-primary-700 text-white rounded-full shadow-lg hover:shadow-xl transition-all transform hover:scale-110 flex items-center justify-center"
        aria-label="Toggle chat"
      >
        {isOpen ? (
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
          </svg>
        ) : (
          <svg className="w-6 h-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
          </svg>
        )}
      </button>

      {/* Chat Panel */}
      {isOpen && (
        <div className="fixed bottom-24 right-6 z-50 w-96 h-[600px] bg-white rounded-2xl shadow-2xl border border-neutral-200 flex flex-col overflow-hidden">
          {/* Header */}
          <div className="bg-gradient-to-r from-primary-500 to-primary-700 text-white p-4 flex items-center justify-between">
            <div>
              <h3 className="font-semibold text-lg">AI Grant Assistant</h3>
              <p className="text-xs text-primary-100">Ask me anything about funding</p>
            </div>
            <button
              onClick={handleNewChat}
              className="p-2 hover:bg-white/20 rounded-lg transition"
              title="New conversation"
            >
              <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 4v16m8-8H4" />
              </svg>
            </button>
          </div>

          {/* Messages */}
          <div className="flex-1 overflow-y-auto p-4 space-y-4">
            {messages.length === 0 ? (
              <div className="text-center py-12">
                <div className="w-16 h-16 bg-primary-100 rounded-full flex items-center justify-center mx-auto mb-4">
                  <svg className="w-8 h-8 text-primary-600" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 10h.01M12 10h.01M16 10h.01M9 16H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-5l-5 5v-5z" />
                  </svg>
                </div>
                <h4 className="font-semibold text-neutral-900 mb-2">Start a conversation</h4>
                <p className="text-sm text-neutral-600 mb-4">Ask me to find grants, explain eligibility, or provide recommendations.</p>
                <div className="space-y-2">
                  <button
                    onClick={() => setInput('What are the latest NSF opportunities?')}
                    className="w-full text-left p-3 bg-neutral-50 hover:bg-primary-50 border border-neutral-200 hover:border-primary-300 rounded-lg text-sm transition"
                  >
                    💡 What are the latest NSF opportunities?
                  </button>
                  <button
                    onClick={() => setInput('Find grants for AI research')}
                    className="w-full text-left p-3 bg-neutral-50 hover:bg-primary-50 border border-neutral-200 hover:border-primary-300 rounded-lg text-sm transition"
                  >
                    🔬 Find grants for AI research
                  </button>
                </div>
              </div>
            ) : (
              messages.map((message) => (
                <div
                  key={message.id}
                  className={`flex ${message.role === 'user' ? 'justify-end' : 'justify-start'}`}
                >
                  <div
                    className={`max-w-[80%] rounded-2xl px-4 py-3 ${
                      message.role === 'user'
                        ? 'bg-primary-500 text-white'
                        : 'bg-neutral-100 text-neutral-900'
                    }`}
                  >
                    <p className="text-sm whitespace-pre-wrap">{message.content}</p>
                    <p className={`text-xs mt-1 ${message.role === 'user' ? 'text-primary-100' : 'text-neutral-500'}`}>
                      {new Date(message.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                    </p>
                  </div>
                </div>
              ))
            )}
            {isLoading && (
              <div className="flex justify-start">
                <div className="bg-neutral-100 rounded-2xl px-4 py-3">
                  <div className="flex gap-1">
                    <div className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style={{ animationDelay: '0ms' }}></div>
                    <div className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style={{ animationDelay: '150ms' }}></div>
                    <div className="w-2 h-2 bg-neutral-400 rounded-full animate-bounce" style={{ animationDelay: '300ms' }}></div>
                  </div>
                </div>
              </div>
            )}
            <div ref={messagesEndRef} />
          </div>

          {/* Input */}
          <form onSubmit={handleSubmit} className="p-4 border-t bg-neutral-50">
            <div className="flex gap-2">
              <input
                type="text"
                value={input}
                onChange={(e) => setInput(e.target.value)}
                placeholder="Ask about grants..."
                className="flex-1 px-4 py-3 border border-neutral-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary-500 focus:border-transparent"
                disabled={isLoading}
              />
              <button
                type="submit"
                disabled={!input.trim() || isLoading}
                className="px-4 py-3 bg-primary-500 text-white rounded-xl hover:bg-primary-600 disabled:opacity-50 disabled:cursor-not-allowed transition"
              >
                <svg className="w-5 h-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 19l9 2-9-18-9 18 9-2zm0 0v-8" />
                </svg>
              </button>
            </div>
          </form>
        </div>
      )}
    </>
  )
}
