import React, { useContext, useEffect, useState } from "react"
import type { Collection } from "../../types/Collection"
import axios from "axios"
import CollectionCard from "./CollectionCard"
import type { Movie } from "../../types/Movie"
import MovieCard from "./MovieCard"
import { WebSocketContext } from "./App"

const CollectionList = (props: { currentLibraryId: number | null}) => {
    const [ collections, setCollections ] = useState<Collection[]>([])
    const [ currentCollection, setCurrentCollection ] = useState<Collection | null>(null)
    const [ movies, setMovies ] = useState<Movie[]>([])

    const websocketMessage = useContext(WebSocketContext)

    const fetchCollections = () => {
        if(props.currentLibraryId) {
            axios.get(`/api/collections/${props.currentLibraryId}`)
            .then(response => {
                if(response.status === 200) {
                    setCollections(response.data)
                }
            })
        } else {
            setCollections([])
            setCurrentCollection(null)
        }
    }

    const fetchMovies = () => {
        if(currentCollection) {
            axios.get(`/api/movies/collection/${currentCollection.id}`)
            .then(response => {
                if (response.status === 200) {
                    setMovies(response.data)
                }
            })
        } else setMovies([])
    }

    useEffect(() => {
        fetchCollections()
    }, [props.currentLibraryId])

    useEffect(() => {
        if(currentCollection) {
            fetchMovies()
        }
    }, [currentCollection])

    useEffect(() => {
            console.log(websocketMessage.message)
            switch(websocketMessage.message) {
                case "movies-updated":
                    fetchMovies()
                    break
                case "collections-updated":
                    fetchCollections()
                    break
            }
        }, [websocketMessage])

    return (
        <>
        {   
            currentCollection !== null
            ? <>
                <p onClick={() => { setCurrentCollection(null) }}>Back</p>
                {
                    movies.map(movie => {
                        return (
                            <MovieCard movie={movie} />
                        )
                    })
                }
            </>
            : collections.map(collection => {
                return (
                    <CollectionCard collection={collection} key={collection.id} setCurrentCollection={setCurrentCollection} />
                )
            })
        }
        </>
    )
}

export default CollectionList