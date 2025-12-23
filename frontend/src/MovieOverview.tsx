import React, { useEffect, useState } from "react"
import type { Movie } from "../../types/Movie"
import axios from "axios"
import MovieCard from "./MovieCard"
import type { Library } from "../../types/Library"
import { ModifyLibrary } from "./ModifyLibrary"
import './MovieOverview.css'

import EditIcon from '@mui/icons-material/Edit'
import AddIcon from '@mui/icons-material/Add'
import { Margin } from "@mui/icons-material"

export const MovieOverview = () => {
    const [ libraries, setLibraries ] = useState<Library[]>([])
    const [ currentLibraryId, setCurrentLibraryId ] = useState<number | null>(null)
    const [ movies, setMovies ] = useState<Movie[]>([])
    const [ editingLibrayId, setEditingLibraryId ] = useState<null | number>(null)
    const [ showModifyLibraryDialog, setShowModifyLibraryDialog ] = useState<boolean>(false)

    const socket = new WebSocket("/api/ws")

    socket.onmessage = (event => {
        const msg = JSON.parse(event.data)

        if (msg.type === 'movies-updated') {
            loadMovies()
        } else if (msg.type === 'libraries-updated') {
            loadLibraries()
            loadMovies()
        }
    })

    const loadMovies = () => {
        if(currentLibraryId) {
            axios.get(`/api/movies/${currentLibraryId}`)
            .then(response => {
                if (response.status === 200) {
                    setMovies(response.data)
                }
            })
        }
    }

    const loadLibraries = () => {
        axios.get('/api/libraries')
        .then(response => {
            if (response.status === 200) {
                let newLibraries = response.data as Library[]
                setLibraries(newLibraries)
                setCurrentLibraryId(newLibraries[0]?.id ?? null)
                loadMovies()
            }
        })
    }

    useEffect(() => {
        loadLibraries()
        loadMovies()
    }, [])

    useEffect(() => {
        loadMovies()
    }, [currentLibraryId])

    return (
        <>
            <div className="contentWrapper">
                <div className="header">
                    {
                        libraries.map(library => {
                            return (
                                <p className={`libraryMenuItem${library.id === currentLibraryId ? " selected" : ""}`} key={library.id} onClick={() => {currentLibraryId !== library.id ? setCurrentLibraryId(library.id) : null}}>
                                    <span className="libraryName">{library.name}</span>
                                    <EditIcon className="editIcon" onClick={() => {
                                        setEditingLibraryId(library.id)
                                        setShowModifyLibraryDialog(true)
                                    }} />
                                </p>
                            )
                        })
                    }
                    <AddIcon className="addIcon" onClick={() => {
                        setEditingLibraryId(null)
                        setShowModifyLibraryDialog(true)
                    }} style={{marginLeft: '20px'}} />
                </div>
                <div className="movieOverview">
                    {
                        movies.map(movie => {
                            return (
                                <MovieCard movie={movie} key={movie.id} />
                            )
                        })
                    }
                </div>
            </div>
            {
                showModifyLibraryDialog === true 
                    ? <ModifyLibrary libraryId={editingLibrayId} setShowModifyLibraryDialog={setShowModifyLibraryDialog} />
                    : null
            }
        </>
    )
}