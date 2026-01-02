import React, { useState, type Dispatch, type SetStateAction } from "react"
import './Menu.css'
import type { Library } from "../../types/Library"
import EditIcon from '@mui/icons-material/Edit'
import AddIcon from '@mui/icons-material/Add'
import SettingsIcon from '@mui/icons-material/Settings'
import LoopIcon from '@mui/icons-material/Loop';

import { ModifyLibrary } from "./ModifyLibrary"
import { ModifySettings } from "./ModifySettings"
import axios from "axios"

export const Menu = (props: { libraries: Library[], currentLibraryId: number | null, setCurrentLibraryId: Dispatch<SetStateAction<number | null>> }) => {
    const [ editingLibrayId, setEditingLibraryId ] = useState<null | number>(null)
    const [ showModifyLibraryDialog, setShowModifyLibraryDialog ] = useState<boolean>(false)
    const [ showModifySettingsDialog, setShowModifySettingsDialog ] = useState<boolean>(false)

    const startScanMetadata = () => {
        axios.post('/api/scan/start')
    }

    return (
        <>
            <div className="menu">
                <div className="menuItems">
                    
                    {
                        props.libraries.map(library => {
                            return (
                                <p className={`libraryMenuItem${library.id === props.currentLibraryId ? " selected" : ""}`} key={library.id} onClick={() => { props.currentLibraryId !== library.id ? props.setCurrentLibraryId(library.id) : null }}>
                                    <span className="libraryName">{library.name}</span>
                                    <span className="actionsWrapper">
                                        <LoopIcon className="scanIcon" onClick={startScanMetadata} />
                                        <EditIcon className="editIcon" onClick={() => {
                                            setEditingLibraryId(library.id)
                                            setShowModifyLibraryDialog(true)
                                        }} />
                                    </span>
                                </p>
                            )
                        })
                    }
                </div>
                <div className="buttons">
                    <AddIcon className="buttonIcon" onClick={() => {
                        setEditingLibraryId(null)
                        setShowModifyLibraryDialog(true)
                    }} />
                    <SettingsIcon className="buttonIcon" onClick={() => { setShowModifySettingsDialog(true) }} />
                </div>
            </div>
            {
                showModifyLibraryDialog === true 
                ? <ModifyLibrary libraryId={editingLibrayId} setShowModifyLibraryDialog={setShowModifyLibraryDialog} />
                : null
            }
            {
                showModifySettingsDialog === true
                ? <ModifySettings setShowModifySettingsDialog={setShowModifySettingsDialog} />
                : null
            }
        </>
    )
}