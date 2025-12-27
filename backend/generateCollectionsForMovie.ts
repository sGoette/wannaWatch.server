import { DatabaseSync } from 'node:sqlite'
import type { Movie } from '../types/Movie'
import path from 'path'
import type { Library } from '../types/Library'
import type { FolderConfig } from '../types/FolderConfig'
import type { Collection } from '../types/Collection'
import type { MovieCollection } from '../types/MovieCollection'
import { copyFile, readFile } from 'fs/promises'
import crypto from 'crypto'
import { readdir } from 'fs/promises'
import { MOVIE_THUMBNAIL_LOCATION } from './server.js'

export const generateCollectionsForMovie = async (movieId: number, database: DatabaseSync, MOVIE_LOCATION: string) => {
    database.open()
    const movie = database.prepare(`SELECT * FROM movies WHERE id = ?`).get(movieId) as Movie
    const library = database.prepare(`SELECT * FROM libraries WHERE id = ?`).get(movie.library_id) as Library
    database.close()

    const relativeMoviePath = path.dirname(movie.file_location)
    const folderBasedCollectionTitle: string | null = await scanForConfig(relativeMoviePath, 'wannawatch.json', MOVIE_LOCATION) //this is the base folder in which the collection folders sit

    if(folderBasedCollectionTitle) {
        const pathArray = movie.file_location.split("/")
        const collectionTitle = pathArray[pathArray.indexOf(folderBasedCollectionTitle) + 1]!
        const collectionFolder = pathArray.slice(0, pathArray.indexOf(collectionTitle) + 1).join('/')
        
        database.open()
        const existingCollection = database.prepare('SELECT * FROM collections WHERE title = ? AND library_id = ?').get(collectionTitle, library.id) as Collection | undefined
        database.close()

        if(existingCollection) {
            database.open()
            const existingMovieCollectionMap = database.prepare('SELECT * FROM movies__collections WHERE movie_id = ? AND collection_id = ? ').get(movie.id, existingCollection.id) as MovieCollection | undefined
            database.close()

            if(!existingMovieCollectionMap) {
                database.open()
                database.prepare('INSERT INTO movies__collections (movie_id, collection_id) VALUES (?, ?)').run(movie.id, existingCollection.id)
                database.close()
            }
        } else {
            const thumbnail_file_name = await searchForThumbnail(path.join(MOVIE_LOCATION, collectionFolder))
            database.open()
            const newCollection = database.prepare('INSERT INTO collections (title, thumbnail_file_name, library_id) VALUES (?, ?, ?)').run(collectionTitle, thumbnail_file_name, library.id)
            database.prepare('INSERT INTO movies__collections (movie_id, collection_id) VALUES (?, ?)').run(movie.id, newCollection.lastInsertRowid)
            database.close()
        }
    }
}

const scanForConfig = async (
    startDir: string,
    fileName: string,
    MOVIE_LOCATION: string
    ): Promise<string | null> => {
    const filePath = path.join(MOVIE_LOCATION, startDir, fileName)

    try {
        const content = await readFile(filePath, "utf-8")
        const config = JSON.parse(content) as FolderConfig
        if(config.subfoldersAreCollections) {
            return path.basename(startDir) as string
        } 
        else return null
    } catch (err: any) {
        // File not found → try parent directory
        if (err.code === "ENOENT") {
            const parentDir = path.dirname(startDir)

            // Reached top-most folder
            if (parentDir === startDir) {
                return null
            }

            return scanForConfig(parentDir, fileName, MOVIE_LOCATION)
        }

        // Any other error (e.g. invalid JSON) should propagate
        throw err
    }
}

const searchForThumbnail = async (collectionFolder: string): Promise<string> => {
    const files = await readdir(collectionFolder)
    const collectionThumnail = files.find(file => ['collection'].includes(path.parse(file).name))

    if(collectionThumnail) {
        const hash = crypto.createHash('sha256')
        hash.update(new Date().toLocaleTimeString() + collectionThumnail)
        const thumbnailFileName = hash.digest('hex')
        const thumbnailRelativeDestination = `${thumbnailFileName}${path.extname(collectionThumnail)}`
        await copyFile(path.join(collectionFolder, collectionThumnail), path.join(MOVIE_THUMBNAIL_LOCATION, thumbnailRelativeDestination))
        return thumbnailRelativeDestination
    }

    return ""
}