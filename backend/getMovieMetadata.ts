import { execFile } from "node:child_process"
import { promisify } from "node:util"
import path from "node:path"
import fs from "node:fs/promises"
import crypto from 'crypto'

const execFileAsync = promisify(execFile)

export interface MovieMetadata {
    duration: number // seconds
    width?: number
    height?: number
    codec?: string
    format?: string
    path: string
    thumbnailPath?: string
}

export async function getMovieMetadata(filePath: string, MOVIE_THUMBNAIL_LOCATION: string): Promise<MovieMetadata> {
    await fs.mkdir(MOVIE_THUMBNAIL_LOCATION, { recursive: true })
    try {
        const { stdout } = await execFileAsync("ffprobe", [
            "-v", "quiet",
            "-print_format", "json",
            "-show_format",
            "-show_streams",
            filePath
        ])

        const data = JSON.parse(stdout)

        // Find the first video stream
        const videoStream = data.streams.find((s: any) => s.codec_type === "video")

        const metadata: MovieMetadata = {
            path: filePath,
            duration: parseFloat(data.format.duration), // seconds
            width: videoStream?.width,
            height: videoStream?.height,
            codec: videoStream?.codec_name,
            format: data.format.format_name,
        }

        const randomTime = Math.floor(metadata.duration * (0.05 + Math.random() * 0.85))

        // Output file
        const hash = crypto.createHash('sha256')
        hash.update(new Date().toLocaleTimeString() + filePath)
        const thumbnailFileName = hash.digest('hex')
        const fileName = thumbnailFileName + ".jpg"
        const outputPath = path.join(MOVIE_THUMBNAIL_LOCATION, fileName)

        await execFileAsync("ffmpeg", [
            "-ss",
            randomTime.toString(),
            "-i",
            filePath,
            "-frames:v",
            "1",
            "-q:v",
            "2", // quality 2 = good
            outputPath,
        ])

        metadata.thumbnailPath = fileName

        return metadata
    } catch (err) {
        console.error("Error getting metadata for", filePath, err)
        throw err
    }
}