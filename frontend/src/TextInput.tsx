import React, { useState } from "react"

export const TextInput = (props: { label: string, value: string, SettingKey: string, setValue: (key: string, value: string) => void }) => {
    const [ value, setValue ] = useState<string>(props.value)
    return (
        <div className="inputWrapper">
            <label>{props.label}</label>
            <input type="text" value={value} onChange={(e) => {
                props.setValue(props.SettingKey, e.target.value)
                setValue(e.target.value)
            }} />
        </div>
    )
}