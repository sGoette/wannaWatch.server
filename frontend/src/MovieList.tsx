import React, { useEffect, useState } from "react"
import MovieCard from "./MovieCard"
import type { Movie } from "../../types/Movie"
import axios from "axios"

const MovieList = (props: { currentLibraryId: number | null}) => {
    const [ movies, setMovies ] = useState<Movie[]>([])

    const loadMovies = () => {
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
        loadMovies()
    }, [props.currentLibraryId])

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