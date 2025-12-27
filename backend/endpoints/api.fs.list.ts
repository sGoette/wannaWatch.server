import type { FastifyInstance } from 'fastify'
import { readdir } from 'fs/promises'
import path from "path"

const API_FS_LIST_GET = (fastify: FastifyInstance, MOVIE_LOCATION: string) => {
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
}

export default API_FS_LIST_GET