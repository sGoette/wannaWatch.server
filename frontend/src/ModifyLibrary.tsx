import React, { useEffect, useState } from "react"
import type { Library } from "../../types/Library"
import "./Dialog.css"
import axios from "axios"

import HourglassBottomIcon from '@mui/icons-material/HourglassBottom'
import CloseIcon from '@mui/icons-material/Close'

import { Folder } from "./Folder"


export const ModifyLibrary = (props: { libraryId: number | null, setShowModifyLibraryDialog: (arg0: boolean) => void }) => {
    const [ library, setLibrary ] = useState<null | Library>()
    const [ libraryName, setLibraryName ] = useState<string>("")
    const [ libraryMediaFolder, setLibraryMediaFolder ] = useState<string>("")

    const saveLibrary = () => {
        const newLibrary = {id: props.libraryId, name: libraryName, media_folder: libraryMediaFolder} as Library

        if(props.libraryId) {
            axios.post('/api/library', newLibrary)
            .then(response => {
                if(response.status === 200) {
                    props.setShowModifyLibraryDialog(false)
                }
            })
        } else {
            axios.put('/api/library', newLibrary)
            .then(response => {
                if(response.status === 200) {
                    props.setShowModifyLibraryDialog(false)
                }
            })
        }
    }

    const deleteLibrary = () => {
        if(props.libraryId) {
            axios.delete(`/api/library/${props.libraryId}`)
            .then(response => {
                if(response.status === 200) {
                    props.setShowModifyLibraryDialog(false)
                }
            })
        }
    }

    useEffect(() => {
        if(props.libraryId) {
            axios.get(`/api/library/${props.libraryId}`)
            .then(response => {
                if(response.status === 200) {
                    let libraryData = response.data as Library
                    setLibrary(libraryData)
                    setLibraryName(libraryData.name)
                    setLibraryMediaFolder(libraryData.media_folder)
                }
            })
        }
    }, [])

    return (
        <div className="dialogWrapper">
            {
                library !== null
                ? <div className="dialogBox">
                    <div className="closeButtonWrapper">
                        <CloseIcon className="closeButton" onClick={() => { props.setShowModifyLibraryDialog(false) }} />
                    </div>
                    <div className="inputList">
                        <input type="text" value={libraryName} onChange={(e) => setLibraryName(e.target.value)} />
                        <input type="text" value={libraryMediaFolder} onChange={(e) => setLibraryMediaFolder(e.target.value)} disabled />
                        <div className="folderSelectWrapper">
                            <Folder name="Root" path="" libraryMediaFolder={libraryMediaFolder} setLibraryMediaFolder={setLibraryMediaFolder} />
                        </div>
                        <div className="dialogButtonWrapper">
                            <button className="destructive" onClick={() => { props.setShowModifyLibraryDialog(false) }}>Cancel</button>
                            <button className="primary" onClick={saveLibrary} disabled={libraryName === "" || libraryMediaFolder === ""}>Save</button>
                        </div>
                        {
                            props.libraryId
                            ? <button className="destructive" onClick={deleteLibrary}>Delete Library</button>
                            : null
                        }
                    </div>
                </div>
                : <HourglassBottomIcon />
            }
        </div>
    )
}