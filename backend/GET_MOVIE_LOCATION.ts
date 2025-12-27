import { DatabaseSync } from 'node:sqlite'
import { DATABASE_LOCATION } from './server.js'

const GET_MOVIE_LOCATION = (): string => {
    const db = new DatabaseSync(DATABASE_LOCATION, { open: false })

    db.open()
    const result = db.prepare(`SELECT value FROM settings WHERE key = 'MOVIE_LOCATION'`).get() as { value: string }
    console.log(result)
    db.close()
    return result.value
}

export default GET_MOVIE_LOCATION