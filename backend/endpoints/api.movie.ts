import type { FastifyInstance } from "fastify"
import { DatabaseSync } from 'node:sqlite'
import path from "path"
import { statSync, createReadStream } from 'fs'
import { readFile } from "fs/promises"
import mime from "mime-types"

export const API_MOVIE_GET = (fastify: FastifyInstance, database: DatabaseSync) => {
    fastify.get('/api/movie/:movieId', async (request, reply) => {
        const { movieId } = request.params as { movieId: number }

        database.open()
        const movie = database.prepare(`SELECT * FROM movies WHERE id = ?`).get(movieId)
        database.close()
        reply.type('application/json').code(200)
        return movie
    })
}

export const API_MOVIE_STREAM_GET = (fastify: FastifyInstance, database: DatabaseSync, MOVIE_LOCATION: string) => {
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
}

export const API_MOVIES_THUMBNAIL_GET = (fastify: FastifyInstance, MOVIE_THUMBNAIL_LOCATION: string) => {
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
}