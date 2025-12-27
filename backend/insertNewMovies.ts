import { DatabaseSync } from 'node:sqlite'
import { getMovieMetadata, type MovieMetadata } from './getMovieMetadata.js'
import type { Library } from '../types/Library.js'
import { scanDirectoryForNewMovies } from './scanDirectoryForNewMovies.js'
import path from "path"
import { generateCollectionsForMovie } from './generateCollectionsForMovie.js'
import GET_MOVIE_LOCATION from './GET_MOVIE_LOCATION.js'

export const insertNewMovies = (database: DatabaseSync, MOVIE_THUMBNAIL_LOCATION: string, libraryId?: number): Promise<void | MovieMetadata>[] => {
    const MOVIE_LOCATION = GET_MOVIE_LOCATION()
    database.open()
    const libraries = database.prepare('SELECT * FROM libraries').all() as Library[]
    database.close()

    let promisses: Promise<void | MovieMetadata>[] = []
    libraries
    .filter(library => !libraryId || library.id === libraryId)
    .forEach(async library => {
        let movies = await scanDirectoryForNewMovies(library.media_folder, database, library.id, MOVIE_LOCATION)

        promisses.concat(movies.map(async movie => {
            const metaData = await getMovieMetadata(movie, MOVIE_THUMBNAIL_LOCATION)
            const title = path.parse(movie).name.toLowerCase().split(' ').map(word => word.charAt(0).toUpperCase() + word.substring(1)).join(' ')
            const file_location = path.relative(MOVIE_LOCATION, movie)
            database.open()
            const insertedMovie = database
            .prepare(`
                            INSERT INTO movies 
                            (title, file_location, length_in_seconds, width, height, codec, format, thumbnail_file_name, library_id)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)`
            )
            .run(title, file_location, metaData.duration, metaData.width ?? 0, metaData.height ?? 0, metaData.codec ?? "", metaData.format ?? "", metaData.thumbnailPath ?? "", library.id)
            database.close()
            generateCollectionsForMovie(Number(insertedMovie.lastInsertRowid), database)
        }))
    })

    return promisses
}