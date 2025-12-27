import type { FastifyInstance } from "fastify"
import { DatabaseSync } from 'node:sqlite'
import type { Setting } from "../../types/Setting"
import GET_MOVIE_LOCATION from "../GET_MOVIE_LOCATION.js"


export const API_SETTINGS_GET = (fastify: FastifyInstance, database: DatabaseSync) => {
    fastify.get("/api/settings", async (request, reply) => {
        database.open()
        const settings = database.prepare('SELECT * FROM settings ORDER BY key ASC').all() as Setting[]
        database.close()

        reply.type('application/json').code(200)
        return settings
    })
}

export const API_SETTINGS_POST = (fastify: FastifyInstance, database: DatabaseSync) => {
    fastify.post("/api/settings", async (request, reply) => {
        if (!request.body) {
            reply.code(400).send('Missing Body')
            return
        }

        const settings = request.body as Setting[]

        database.open()
        settings.forEach(setting => {
            database.prepare('UPDATE settings SET value = ? WHERE key = ?').run(setting.value, setting.key)
        })
        database.close()
        //DELETE ALL LIBRARIES WHEN THIS HAPPENS???
    })
}