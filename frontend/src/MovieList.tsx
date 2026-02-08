import React, { useContext, useEffect, useState } from "react"
import MovieCard from "./MovieCard"
import type { Movie } from "../../types/Movie"
import axios from "axios"
import { WebSocketContext } from "./App"

const MovieList = (props: { currentLibraryId: number | null}) => {
    const [ movies, setMovies ] = useState<Movie[]>([])
    const websocketMessage = useContext(WebSocketContext)

    const fetchMovies = () => {
        if(props.currentLibraryId) {
            axios.get(`/api/movies/${props.currentLibraryId}`)
            .then(response => {
                if (response.status === 200) {
                    setMovies(response.data)
                }
            })
        }
    }

    useEffect(() => {
        fetchMovies()
    }, [props.currentLibraryId])

    useEffect(() => {
            console.log(websocketMessage.message)
            switch(websocketMessage.message) {
                case "movies-updated": 
                    fetchMovies()
                    break
            }
        }, [websocketMessage])

    return (
        <>
        { 
            movies.map(movie => {
                return (
                    <MovieCard movie={movie} key={movie.id} />
                )
            })
        }
        </>
    )
}

export default MovieList