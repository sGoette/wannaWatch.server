import React, { useEffect, useRef, useState } from "react"
import { useParams } from "react-router"

interface VideoPlayerProps {
    autoPlay?: boolean
    startAtSeconds?: number
}

export const MoviePlayer = ({
    autoPlay = true,
    startAtSeconds = 0,
}: VideoPlayerProps) => {
    let { movieId } = useParams()
    const videoRef = useRef<HTMLVideoElement>(null)

    const src = `/api/movie/${movieId}/stream`

    useEffect(() => {
        const video = videoRef.current
        if (!video) return

        const onLoadedMetadata = () => {
            if (startAtSeconds > 0) {
                video.currentTime = startAtSeconds
            }
        }

        video.addEventListener("loadedmetadata", onLoadedMetadata)

        return () => {
            video.removeEventListener("loadedmetadata", onLoadedMetadata)
        };
    }, [movieId, startAtSeconds])

    return (
        <div style={{ width: "100%", background: "#000" }}>
            <video
                ref={videoRef}
                src={src}
                controls
                autoPlay={autoPlay}
                style={{ width: "100%" }}
                preload="metadata"
            />
        </div>
    )
}