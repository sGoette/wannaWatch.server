import { type FastifyInstance } from "fastify"
import { DatabaseSync } from 'node:sqlite'

export const API_COLLECTION_MOVIES = (fastify: FastifyInstance, database: DatabaseSync) => {
    fastify.get('/api/collection/movies/:collectionId', async (request, reply) => {
        const { collectionId } = request.params as { collectionId: string }
        database.open()
        const movies = database.prepare(`
            SELECT * 
            FROM movies 
            WHERE id IN (
                SELECT movie_id 
                FROM movies__collections
                WHERE collection_id = ?
            )`).all(collectionId)
        database.close()

        reply.type('application/json').code(200)
        return movies
    })
}