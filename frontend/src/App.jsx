import { useState } from 'react'
import { Route, Routes } from 'react-router-dom'
import Home from './Home'
import Chat from './components/Chat'
// import './App.css'

function App() {

  return (
    <>
      <Routes>
        <Route path="/" element={<Home />} />
        <Route path="/chat" element={<Chat/>} />
      </Routes>
    </>
  )
}

export default App
