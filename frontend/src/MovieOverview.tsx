import React, { useEffect, useState } from "react"
import type { Movie } from "../../types/Movie"
import axios from "axios"
import MovieCard from "./MovieCard"
import type { Library } from "../../types/Library"
import './MovieOverview.css'


import { Menu } from "./Menu"

export const MovieOverview = () => {
    const [ libraries, setLibraries ] = useState<Library[]>([])
    const [ currentLibraryId, setCurrentLibraryId ] = useState<number | null>(null)
    const [ movies, setMovies ] = useState<Movie[]>([])

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
                <Menu libraries={libraries} currentLibraryId={currentLibraryId} setCurrentLibraryId={setCurrentLibraryId} />
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
        </>
    )
}