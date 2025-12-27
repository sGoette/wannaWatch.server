import type { FastifyInstance } from "fastify"
import { DatabaseSync } from 'node:sqlite'

const API_LIBRARIES_GET = (fastify: FastifyInstance, database: DatabaseSync) => {
    fastify.get('/api/libraries', async (request, reply) => {
        database.open()
        const libraries = database.prepare('SELECT * FROM libraries ORDER BY name ASC').all()
        database.close()
        reply.type('application/json').code(200)
        return libraries
    })
}

export default API_LIBRARIES_GET