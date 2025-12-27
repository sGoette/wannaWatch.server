import React, { useContext, useEffect, useState } from "react"
import type { Movie } from "../../types/Movie"
import axios from "axios"
import MovieCard from "./MovieCard"
import type { Library } from "../../types/Library"
import './MovieOverview.css'
import { Menu } from "./Menu"
import { WebSocketContext } from "./App"
import MovieList from "./MovieList"
import CollectionList from "./CollectionList"

enum LibraryDisplayMode {
    COLLECTIONS = "COLLECTION",
    MOVIES = "MOVIES"
}

export const MovieOverview = () => {
    const [ libraries, setLibraries ] = useState<Library[]>([])
    const [ currentLibraryId, setCurrentLibraryId ] = useState<number | null>(null)
    const [ movies, setMovies ] = useState<Movie[]>([])
    const [ libraryDisplayMode, setLibraryDisplayMode ] = useState<LibraryDisplayMode>(LibraryDisplayMode.COLLECTIONS)

    const websocketMessage = useContext(WebSocketContext)

    const loadLibraries = () => {
        axios.get('/api/libraries')
        .then(response => {
            if (response.status === 200) {
                let newLibraries = response.data as Library[]
                setLibraries(newLibraries)
                setCurrentLibraryId(newLibraries[0]?.id ?? null)
            }
        })
    }

    useEffect(() => {
        loadLibraries()
    }, [])

    useEffect(() => {
        console.log(websocketMessage.message)
        switch(websocketMessage.message) {
            case "libraries-updated": 
                loadLibraries()
                break

            case "movies_updated": 
                break
        }
    }, [websocketMessage])

    return (
        <>
            <div className="contentWrapper">
                <Menu libraries={libraries} currentLibraryId={currentLibraryId} setCurrentLibraryId={setCurrentLibraryId} />
                <div className="contentContainer">
                    <div className="header">
                        <p className={`headerItem${libraryDisplayMode === LibraryDisplayMode.COLLECTIONS ? " active" : ""}`} onClick={() => { setLibraryDisplayMode(LibraryDisplayMode.COLLECTIONS) }}>Collections</p>
                        <p className={`headerItem${libraryDisplayMode === LibraryDisplayMode.MOVIES ? " active" : ""}`} onClick={() => { setLibraryDisplayMode(LibraryDisplayMode.MOVIES) }}>Movies</p>
                    </div>
                    <div className="movieOverview">
                        {(() => {
                            switch(libraryDisplayMode) {
                                case LibraryDisplayMode.COLLECTIONS: return <CollectionList currentLibraryId={currentLibraryId} />
                                case LibraryDisplayMode.MOVIES: return <MovieList currentLibraryId={currentLibraryId} />
                                default: return null
                            }
                        })()}
                    </div>
                </div>
            </div>
        </>
    )
}