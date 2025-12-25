import fs from "node:fs/promises"
import path from "node:path"
import type { DatabaseSync } from "node:sqlite"

// List of video extensions to detect
const VIDEO_EXTENSIONS = [".mp4", ".mkv", ".mov", ".avi", ".webm", ".m4v"]

export const scanDirectoryForNewMovies = async (folder: string, database: DatabaseSync, libraryId: number, MOVIE_LOCATION: string): Promise<string[]> => {
  const results: string[] = []

  const recursiveScan = async (dir: string) => {
    const entries = await fs.readdir(dir, { withFileTypes: true })

    for (const entry of entries) {
      const fullPath = path.join(dir, entry.name)

      if (entry.isDirectory()) {
        await recursiveScan(fullPath)
      } else if (entry.isFile()) {
        const ext = path.extname(entry.name).toLowerCase()
        if (VIDEO_EXTENSIONS.includes(ext)) {
          const filePath = path.relative(MOVIE_LOCATION, fullPath)
          database.open()
          const movieExists = database.prepare(`SELECT file_location FROM movies WHERE file_location = ? AND library_id = ? LIMIT 1`)
          const row = movieExists.get(filePath, libraryId)
          database.close()

          if(row === undefined) {
            results.push(fullPath)
          }
        }
      }
    }
  }

  await recursiveScan(path.join(MOVIE_LOCATION, folder))
  return results
}
