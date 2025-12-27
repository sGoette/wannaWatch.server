import React, { useEffect, useState } from "react"
import type { Collection } from "../../types/Collection"
import axios from "axios"
import CollectionCard from "./CollectionCard"
import type { Movie } from "../../types/Movie"
import MovieCard from "./MovieCard"

const CollectionList = (props: { currentLibraryId: number | null}) => {
    const [ collections, setCollections ] = useState<Collection[]>([])
    const [ currentCollection, setCurrentCollection ] = useState<Collection | null>(null)
    const [ movies, setMovies ] = useState<Movie[]>([])

    const loadCollections = () => {
        if(props.currentLibraryId) {
            axios.get(`/api/collections/${props.currentLibraryId}`)
            .then(response => {
                if(response.status === 200) {
                    setCollections(response.data)
                }
            })
        }
    }

    const loadMovies = () => {
        if(currentCollection) {
            axios.get(`/api/collection/movies/${currentCollection.id}`)
            .then(response => {
                if (response.status === 200) {
                    setMovies(response.data)
                }
            })
        } else setMovies([])
    }

    useEffect(() => {
        loadCollections()
    }, [props.currentLibraryId])

    useEffect(() => {
        if(currentCollection) {
            loadMovies()
        }
    }, [currentCollection])

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