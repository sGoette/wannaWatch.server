// src/App.tsx
import React, { useEffect, useState } from "react"
import { Routes, Route } from "react-router"
import { MovieOverview } from "./MovieOverview"
import { MoviePlayer } from "./MoviePlayer"
import useWebSocket from "react-use-websocket"

export const WebSocketContext: React.Context<{ timestamp: number, message: string }> = React.createContext({timestamp: Date.now(), message: ""})
const SOCKET_URL = "ws://localhost:4000/ws" // "/ws"

const App = () => {
  const [ websocketMessage, setWebsocketMessage ] = useState<{timestamp: number, message: string}>({timestamp: Date.now(), message: ""})
  const { sendMessage, lastMessage, readyState } = useWebSocket(SOCKET_URL)

  useEffect(() => {
    if(lastMessage !== null) {
      const newMessage = JSON.parse(lastMessage.data) as { type: string}
      setWebsocketMessage({ timestamp: Date.now(), message: newMessage.type })
    }
  }, [lastMessage])
  
  return (
    <WebSocketContext.Provider value={websocketMessage}>
      <Routes>
        <Route index path="" element={<MovieOverview />} />
        <Route path="player/:movieId" element={<MoviePlayer />} />
      </Routes>
    </WebSocketContext.Provider>
  )
}

export default App