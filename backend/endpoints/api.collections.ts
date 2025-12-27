import type { FastifyInstance } from "fastify"
import { DatabaseSync } from 'node:sqlite'

export const API_COLLECTIONS_GET = (fastify: FastifyInstance, database: DatabaseSync) => {
    fastify.get('/api/collections/:libraryId', async (request, reply) => {
        const { libraryId } = request.params as { libraryId: string }
        database.open()
        const collections = database.prepare('SELECT * FROM collections WHERE library_id = ?').all(libraryId)
        database.close()

        reply.type('application/json').code(200)
        return collections
    })
}