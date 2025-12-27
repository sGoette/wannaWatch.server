import type { FastifyInstance } from "fastify"
import { DatabaseSync } from 'node:sqlite'
import type { Library } from "../../types/Library"
import sendMessageToClients from "../sendMessageToClients.js"
import type { WebSocket } from "@fastify/websocket"
import { insertNewMovies } from "../insertNewMovies.js"
import type { Movie } from "../../types/Movie"
import { unlink } from 'fs'
import path from 'path'

export const API_LIBRARY_GET = (fastify: FastifyInstance, database: DatabaseSync) => {
    fastify.get('/api/library/:libraryId', async (request, reply) => {
        const { libraryId } = request.params as { libraryId: string }
        database.open()
        const library = database.prepare('SELECT * FROM libraries WHERE id = ?').get(libraryId)
        database.close()

        if (!library) {
            reply.code(404).send('Library not found')
            return
        }

        reply.type('application/json').code(200)
        return library
    })
}

export const API_LIBRARY_POST = (fastify: FastifyInstance, database: DatabaseSync, clients: Set<WebSocket>) => {
    fastify.post('/api/library', async (request, reply) => {
        if (!request.body) {
            reply.code(400).send('Missinb Body')
            return
        }
    
        const library = request.body as Library
    
        database.open()
        database.prepare('UPDATE libraries SET name = ?, media_folder = ? WHERE id = ?').run(library.name, library.media_folder, library.id)
        database.close()
    
        sendMessageToClients(clients, "libraries-updated")
        reply.code(200).send("Library updated")
    })
}

export const API_LIBRARIES_PUT = (fastify: FastifyInstance, database: DatabaseSync, clients: Set<WebSocket>, MOVIE_LOCATION: string, MOVIE_THUMBNAIL_LOCATION: string ) => {
    fastify.put('/api/library', async (request, reply) => {
        if (!request.body) {
            reply.code(400).send('Missing Body')
            return
        }

        const library = request.body as { name: string, media_folder: string }

        database.open()
        const insertLibrary = database.prepare(`
            INSERT INTO libraries
            (name, media_folder)
            VALUES (?, ?)
        `).run(library.name, library.media_folder)
        database.close()
        sendMessageToClients(clients, "libraries-updated")

        Promise.all(insertNewMovies(database, MOVIE_LOCATION, MOVIE_THUMBNAIL_LOCATION)).then(() => {
            sendMessageToClients(clients, "movies-updated")
        })

        reply.code(200).send("Library inserted")
    })
}

export const API_LIBRARY_DELETE = (fastify: FastifyInstance, database: DatabaseSync, clients: Set<WebSocket>, MOVIE_THUMBNAIL_LOCATION: string) => {
    fastify.delete('/api/library/:libraryId', async ( request, reply) => {
        const { libraryId } = request.params as { libraryId: string }
    
        if(!libraryId) {
            reply.code(400).send("Library ID is missing")
            return
        }
    
        database.open()
        const movies = database.prepare('SELECT * FROM movies WHERE library_id = ?').all(libraryId) as Movie[]
        database.close()
    
        const thumbnailDeletionPromisses = movies.map(movie => {
            const thumbnailPath = path.join(MOVIE_THUMBNAIL_LOCATION, movie.thumbnail_file_name)
            return unlink(thumbnailPath, () => {})
        })
    
        Promise.all(thumbnailDeletionPromisses).then(() => {
            database.open()
            database.prepare('DELETE FROM movies WHERE library_id = ?').run(libraryId)
            database.prepare(`
                DELETE FROM movies__collections WHERE collection_id IN (
                    SELECT id FROM collections WHERE library_id = ?
                )
            `).run(libraryId)
            database.prepare('DELETE FROM collections WHERE library_id = ?').run(libraryId)
            database.prepare('DELETE FROM libraries WHERE id = ?').run(libraryId)
            database.close()
            sendMessageToClients(clients, "libraries-updated")
        })
        reply.code(200).send("Started deleting library")
    })
}