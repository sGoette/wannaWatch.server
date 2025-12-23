import React, { useState } from "react"
import FolderIcon from '@mui/icons-material/Folder'
import FolderOpenIcon from '@mui/icons-material/FolderOpen'

import './Folder.css'
import type { FolderEntry } from "../../types/FolderEntry"
import axios from "axios"

export const Folder = (props: { name: string, path: string, libraryMediaFolder: string, setLibraryMediaFolder: (arg0: string) => void }) => {
    const [ subFolders, setSubFolders ] = useState<FolderEntry[]>([])
    const setCurrentFolder = () => {
        props.setLibraryMediaFolder(props.path)

        const params = { path: props.path }
        axios.get('/api/fs/list', { params })
        .then(response => {
            if(response.status === 200) {
                setSubFolders(response.data.entries as FolderEntry[])
            }
        })
    }
    return (
        <div className="folderContainer">
            <div className={`folderRow${props.path === props.libraryMediaFolder ? ' selected' : ""}`} onClick={setCurrentFolder}>
                {
                    subFolders.length > 0
                    ? <FolderOpenIcon className="folderIcon" />
                    : <FolderIcon className="folderIcon" />
                }
                <p>{props.name}</p>
            </div>
            <div className="subFolderContainer">
                {
                    subFolders.map(folder => 
                        <Folder name={folder.name} path={folder.path} libraryMediaFolder={props.libraryMediaFolder} setLibraryMediaFolder={props.setLibraryMediaFolder} key={folder.path} />
                    )
                }
            </div>
        </div>
    )
}