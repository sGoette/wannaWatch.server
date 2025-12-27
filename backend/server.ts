import Fastify from "fastify"
import staticPlugin from '@fastify/static'
import type { WebSocket } from "@fastify/websocket"
import { DatabaseSync } from 'node:sqlite'
import { existsSync, createReadStream } from 'fs'
import initDatabase from "./initDatabase.js"
import path from "path"
import { insertNewMovies } from "./insertNewMovies.js"
import API_FS_LIST_GET from "./endpoints/api.fs.list.js"
import API_LIBRARIES_GET from "./endpoints/api.libraries.js"
import { API_LIBRARIES_PUT, API_LIBRARY_DELETE, API_LIBRARY_GET, API_LIBRARY_POST } from "./endpoints/api.library.js"
import { API_MOVIES_GET } from "./endpoints/api.movies.js"
import { API_MOVIE_STREAM_GET, API_MOVIES_THUMBNAIL_GET } from "./endpoints/api.movie.js"
import { API_SETTINGS_GET, API_SETTINGS_POST } from "./endpoints/api.settings.js"
import sendMessageToClients from "./sendMessageToClients.js"
import type { Movie } from "../types/Movie.js"
import { generateCollectionsForMovie } from "./generateCollectionsForMovie.js"
import { API_COLLECTIONS_GET } from "./endpoints/api.collections.js"
import { API_COLLECTION_MOVIES } from "./endpoints/api.collection.movies.js"

export const DATABASE_LOCATION = '../../data/db/database.sqlite'
export const MOVIE_THUMBNAIL_LOCATION = '../../data/thumbnails'
const FRONTEND_PATH = path.resolve("./frontend")

const fastify = Fastify({ logger: true })

const clients = new Set<WebSocket>()

const database = new DatabaseSync(DATABASE_LOCATION, { open: false })
initDatabase(database)

API_FS_LIST_GET(fastify)

API_LIBRARIES_GET(fastify, database)

API_LIBRARY_GET(fastify, database)

API_LIBRARY_POST(fastify, database, clients)

API_LIBRARIES_PUT(fastify, database, clients)

API_LIBRARY_DELETE(fastify, database, clients)

API_MOVIES_GET(fastify, database)

API_MOVIE_STREAM_GET(fastify, database)

API_MOVIES_THUMBNAIL_GET(fastify)

API_COLLECTIONS_GET(fastify, database)

API_COLLECTION_MOVIES(fastify, database)

API_SETTINGS_GET(fastify, database)

API_SETTINGS_POST(fastify, database)

fastify.get('/api/updateMetadata', async (request, reply) => {
    database.open()
    const movies = database.prepare(`SELECT * FROM movies`).all() as Movie[]
    database.close()

    const promisses = movies.map(async movie => {
        return generateCollectionsForMovie(movie.id, database)
    })

    Promise.all(promisses).then(() => {
        sendMessageToClients(clients, 'movies-updated')
    })

    reply.code(200).send('Start scanning Metadata...')
})

fastify.get('/api/scanDirectories', async (request, response) => {
    Promise.all(insertNewMovies(database, MOVIE_THUMBNAIL_LOCATION)).then(() => {
        sendMessageToClients(clients, "libraries-updated")
        sendMessageToClients(clients, "movies-updated")
    })

    response.code(200).send('Started scanning for movies...')
})

fastify.get("/api/health", async () => {
  return { status: "ok" }
})

fastify.register(import('@fastify/websocket'), {
    options: { perMessageDeflate: false }
})

fastify.register(async (fastify) => {
    fastify.get("/ws", { websocket: true }, (connection, request) => {
        clients.add(connection)
    })
})

fastify.register(staticPlugin, {
    root: FRONTEND_PATH,
    prefix: "/"
})

fastify.setNotFoundHandler((request, reply) => {
    const indexFile = path.join(FRONTEND_PATH, "index.html")

    if (existsSync(indexFile)) {
        reply.type("text/html").send(
            createReadStream(indexFile)
        )
    } else {
        reply.code(404).send("Not found")
    }
})

fastify.listen({ port: 4000, host: "0.0.0.0" }, (err, address) => {
    if (err) throw err
})