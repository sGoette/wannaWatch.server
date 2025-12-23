// src/App.tsx
import React from "react"
import { Routes, Route } from "react-router"
import { MovieOverview } from "./MovieOverview"
import { MoviePlayer } from "./MoviePlayer"

const App = () => {

  return (
    <Routes>
      <Route index path="" element={<MovieOverview />} />
      <Route path="player/:movieId" element={<MoviePlayer />} />
    </Routes>
  )
}

export default App