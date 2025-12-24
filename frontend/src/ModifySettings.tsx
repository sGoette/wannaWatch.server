import React, { useEffect, useState, type Dispatch, type SetStateAction } from "react"
import type { Setting } from "../../types/Setting"
import axios from "axios"
import './Dialog.css'

import CloseIcon from '@mui/icons-material/Close'
import { TextInput } from "./TextInput"

export const ModifySettings = (props: { setShowModifySettingsDialog: Dispatch<SetStateAction<boolean>> }) => {
    const [ settings, setSettings ] = useState<Setting[]>([])

    useEffect(() => {
        axios.get('/api/settings')
        .then(response => {
            if(response.status === 200) {
                let settingsData = response.data as Setting[]
                setSettings(settingsData)
            }
        })
    }, [])

    const setSetting = (key: string, value: string) => {
        var newSettings = settings
        newSettings[newSettings.findIndex(setting => setting.key === key)]!.value = value
        setSettings(newSettings)
    }

    const saveData = () => {
        axios.post('/api/settings', settings)
        .then(response => {
            if(response.status === 200) {
                props.setShowModifySettingsDialog(false)
            }
        })
    }

    return (
        <div className="dialogWrapper">
            <div className="dialogBox">
                <div className="closeButtonWrapper">
                    <CloseIcon className="closeButton" onClick={() => { props.setShowModifySettingsDialog(false) }} />
                </div>
                <div className="inputList">
                {
                    settings.map((setting, index) => 
                        <TextInput label={setting.key} value={setting.value} SettingKey={setting.key} setValue={setSetting} key={setting.key} />
                    )
                }
                <div className="dialogButtonWrapper">
                    <button className="destructive" onClick={() => { props.setShowModifySettingsDialog(false) }}>Cancel</button>
                    <button className="primary" onClick={saveData} disabled={settings.find(setting => setting.value === "") !== undefined}>Save</button>
                </div>
                </div>
            </div>
        </div>
    )
}