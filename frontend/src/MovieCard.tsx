import React from 'react'
import type { Movie } from "../../types/Movie"
import './MovieCard.css'
import { useNavigate } from 'react-router'

export function formatDuration(seconds: number): string {
    const hrs = Math.floor(seconds / 3600)
    const mins = Math.floor((seconds % 3600) / 60)
    const secs = Math.floor(seconds % 60)

    const hh = hrs.toString().padStart(2, "0")
    const mm = mins.toString().padStart(2, "0")
    const ss = secs.toString().padStart(2, "0")

    return `${hrs > 0 ? hh + ":" : ""}${mm}:${ss}`;
}


const MovieCard = (props: {
    movie: Movie
}) => {
    const navigate = useNavigate()
    const openPlayer = () => {
        navigate(`/player/${props.movie.id}`)
    }
    return (
        <div className="movieCard" onClick={openPlayer}>
            <img src={'api/poster/' + props.movie.poster_file_name} alt={props.movie.title} className='thumbnailImage' />
            <div className='metaDataWrapper'>
                <p className='movieTitle'>{props.movie.title}</p>
                <p className='movieDuration'>{formatDuration(props.movie.length_in_seconds)}</p>
            </div>
        </div>
    )
}

export default MovieCard