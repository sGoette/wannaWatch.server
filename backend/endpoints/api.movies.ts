import type { FastifyInstance } from "fastify"
import { DatabaseSync } from 'node:sqlite'

export const API_MOVIES_GET = (fastify: FastifyInstance, database: DatabaseSync) => {
    fastify.get('/api/movies/:libraryId', async (request, response) => {
        const { libraryId } = request.params as { libraryId: number }
        database.open()
        const movies = database.prepare(`SELECT * FROM movies WHERE library_id = ? ORDER BY title ASC`).all(libraryId)
        database.close()
        response.type('application/json').code(200)
        return movies
    })
}