import React, { type Dispatch, type SetStateAction } from "react"
import './MovieCard.css'
import type { Collection } from "../../types/Collection"

const CollectionCard = (props: { collection: Collection, setCurrentCollection: Dispatch<SetStateAction<Collection | null>>}) => {
    return (
        <div className="movieCard" onClick={() => { props.setCurrentCollection(props.collection)}}>
            <img src={'api/poster/' + props.collection.poster_file_name} alt={props.collection.title} className='thumbnailImage' />
            <div className='metaDataWrapper'>
                <p className='movieTitle'>{props.collection.title}</p>
            </div>
        </div>
    )
}

export default CollectionCard