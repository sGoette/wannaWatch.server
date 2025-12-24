import Fastify from "fastify"
import websocket from "@fastify/websocket"
import staticPlugin from '@fastify/static'
import type { WebSocket } from "@fastify/websocket"
import { DatabaseSync } from 'node:sqlite'
import { existsSync, statSync, createReadStream } from 'fs'
import { readdir, readFile } from 'fs/promises'
import type { Library } from "../types/Library"
import initDatabase from "./initDatabase.js"
import path from "path"
import mime from "mime-types"
import { insertNewMovies } from "./insertNewMovies.js"
import type { Setting } from '../types/Setting'

const DATABASE_LOCATION = '../../../data/db/database.sqlite'

const fastify = Fastify({ logger: false })
fastify.register(websocket)
const clients = new Set<WebSocket>()

const database = new DatabaseSync(DATABASE_LOCATION, { open: false })

if (!existsSync(DATABASE_LOCATION)) {
    initDatabase(database)
}

const sendMessageToClients = (msg: string) => {
    for (const client of clients) {
        if (client.readyState === client.OPEN) {
            client.send(JSON.stringify({ type: msg }))
        }
    }
}

const getSettingValueFor = (key: string, database: DatabaseSync): string => {
    database.open()
    const result = database.prepare(`SELECT value FROM settings WHERE key = ?`).get(key) as { value: string }
    database.close()
    return result.value
}

var MOVIE_LOCATION = getSettingValueFor('MOVIE_LOCATION', database)
var MOVIE_THUMBNAIL_LOCATION = getSettingValueFor('MOVIE_THUMBNAIL_LOCATION', database)

fastify.get('/api/fs/list', async (request, reply) => {
    const { path: requestedPath } = request.query as { path?: string }

    const resolvedPath = requestedPath
        ? path.resolve(MOVIE_LOCATION, requestedPath)
        : MOVIE_LOCATION

    // Security: prevent escaping base path
    if (!resolvedPath.startsWith(MOVIE_LOCATION)) {
        reply.code(403).send({ error: "Access denied" })
        return;
    }

    try {
        const entries = await readdir(resolvedPath, { withFileTypes: true })

        const directories = entries
            .filter((e) => e.isDirectory())
            .map((e) => ({
                name: e.name,
                path: path.relative(MOVIE_LOCATION, path.join(resolvedPath, e.name)),
                type: "directory",
            }));

        reply.send({
            path: path.relative(MOVIE_LOCATION, resolvedPath),
            entries: directories,
        })
    } catch (err: any) {
        reply.code(500).send({
            error: "Unable to read directory",
            message: err.message,
        })
    }
})

fastify.get('/api/libraries', async (request, reply) => {
    database.open()
    const libraries = database.prepare('SELECT * FROM libraries ORDER BY name ASC').all()
    database.close()
    reply.type('application/json').code(200)
    return libraries
})

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

fastify.post('/api/library', async (request, reply) => {
    if (!request.body) {
        reply.code(400).send('Missinb Body')
        return
    }

    const library = request.body as Library

    database.open()
    database.prepare('UPDATE libraries SET name = ?, media_folder = ? WHERE id = ?').run(library.name, library.media_folder, library.id)
    database.close()

    sendMessageToClients("libraries-updated")
    reply.code(200).send("Library updated")
})

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
    sendMessageToClients("libraries-updated")

    Promise.all(insertNewMovies(database, MOVIE_LOCATION, MOVIE_THUMBNAIL_LOCATION)).then(() => {
        sendMessageToClients("movies-updated")
    })

    reply.code(200).send("Library inserted")
})

fastify.get('/api/scanDirectories', async (request, response) => {
    Promise.all(insertNewMovies(database, MOVIE_LOCATION, MOVIE_THUMBNAIL_LOCATION)).then(() => {
        sendMessageToClients("libraries-updated")
        sendMessageToClients("movies-updated")
    })

    response.code(200).send('Started scanning for movies...')
})

fastify.get('/api/movies/:libraryId', async (request, response) => {
    const { libraryId } = request.params as { libraryId: number }
    database.open()
    const movies = database.prepare(`SELECT * FROM movies WHERE library_id = ? ORDER BY title ASC`).all(libraryId)
    database.close()
    response.type('application/json').code(200)
    return movies
})

fastify.get('/api/movie/thumbnail/:filename', async (request, reply) => {
    const { filename } = request.params as { filename: string }

    if (filename.includes("..") || filename.includes("/")) {
        reply.status(400).send("Invalid filename")
        return
    }

    const filePath = path.join(MOVIE_THUMBNAIL_LOCATION, filename)

    try {
        const data = await readFile(filePath)

        // Detect MIME type from extension
        const mimeType = mime.lookup(filePath) || "application/octet-stream"

        reply
            .header("Content-Type", mimeType)
            .header("Cache-Control", "public, max-age=86400") // optional caching
            .send(data)
    } catch (err: any) {
        if (err.code === "ENOENT") {
            reply.status(404).send("File not found");
        } else {
            reply.status(500).send("Internal server error");
        }
    }
})

fastify.get('/api/movie/:movieId', async (request, reply) => {
    const { movieId } = request.params as { movieId: number }

    database.open()
    const movie = database.prepare(`SELECT * FROM movies WHERE id = ?`).get(movieId)
    database.close()
    reply.type('application/json').code(200)
    return movie
})

fastify.get("/api/movie/stream/:movieId", async (request, reply) => {
    const { movieId } = request.params as { movieId: number }

    database.open()
    const row = database.prepare(`SELECT file_location FROM movies WHERE id = ?`).get(movieId)
    database.close()

    if (!row) {
        reply.code(404).send("Movie not found")
        return
    }

    const filePath = path.join(MOVIE_LOCATION, row.file_location as string)

    const stat = statSync(filePath)
    const fileSize = stat.size

    const range = request.headers.range
    if (!range) {
        reply.code(416).send("Range header required")
        return
    }

    const match = range.match(/bytes=(\d+)-(\d*)/)
    if (!match) {
        reply.code(416).send("Invalid Range")
        return
    }

    const start = parseInt(match[1] as string, 10)
    const end = match[2]
        ? parseInt(match[2] as string, 10)
        : Math.min(start + 1024 * 1024 * 5, fileSize - 1)

    if (start >= fileSize || end >= fileSize) {
        reply.code(416).send("Range not Satisfiable")
        return
    }

    const chunkSize = end - start + 1

    const stream = createReadStream(filePath, { start, end })

    request.raw.on("close", () => {
        stream.destroy()
    })

    stream.on("error", (err) => {
        console.error("File stream error", err)
        reply.raw.destroy(err)
    })

    reply
        .code(206)
        .type("video/mp4")
        .headers({
            "Content-Range": `bytes ${start}-${end}/${fileSize}`,
            "Accept-Ranges": "bytes",
            "Content-Length": chunkSize.toString(),
            "Content-Type": "video/mp4", // important for Apple TV
            "Cache-Control": "no-cache",
        })
        .send(stream)

    return reply
})

fastify.get("/api/settings", async (request, reply) => {
    database.open()
    const settings = database.prepare('SELECT * FROM settings ORDER BY key ASC').all() as Setting[]
    database.close()

    reply.type('application/json').code(200)
    return settings
})

fastify.post("/api/settings", async (request, reply) => {
    if (!request.body) {
        reply.code(400).send('Missinb Body')
        return
    }

    const settings = request.body as Setting[]

    database.open()
    settings.forEach(setting => {
        database.prepare('UPDATE settings SET value = ? WHERE key = ?').run(setting.value, setting.key)
    })
    database.close()

    const newMovieLocation = settings.find(setting => setting.key === 'MOVIE_LOCATION')?.value
    if(newMovieLocation !== undefined) {
        MOVIE_LOCATION = newMovieLocation
    }

    const newMovieThumbnailLocation = settings.find(setting => setting.key === 'MOVIE_THUMBNAIL_LOCATION')?.value
    if(newMovieThumbnailLocation !== undefined) {
        MOVIE_THUMBNAIL_LOCATION = newMovieThumbnailLocation
    }
    
})

fastify.get("/api/health", async () => {
  return { status: "ok" }
})

fastify.register(async () => {
    fastify.get("/ws", { websocket: true }, (socket, request) => {
        clients.add(socket)
    })
})

const FRONTEND_PATH = path.resolve("../frontend")

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

fastify.listen({ port: 4000 }, (err, address) => {
    if (err) throw err
})