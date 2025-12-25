import { DatabaseSync } from 'node:sqlite'

const initDatabase = (db: DatabaseSync) => {
    db.open()
    db.exec(`
        CREATE TABLE settings (
            key TEXT NOT NULL UNIQUE,
            value TEXT,
            format TEXT NOT NULL
        )
    `)
    db.exec(`
        INSERT INTO settings
        ( key, value, format )
        VALUES
        ( 'MOVIE_LOCATION', '', 'string' )
    `)
    db.exec(`
        CREATE TABLE movies (
            id INTEGER PRIMARY KEY,
            title VARCHAR(255),
            file_location TEXT NOT NULL UNIQUE,
            length_in_seconds INTEGER,
            width INTEGER,
            height INTEGER,
            codec VARCHAR(255),
            format VARCHAR(255),
            thumbnail_file_name TEXT,
            library_id INTEGER
        )  
    `)
    db.exec(`
        CREATE TABLE libraries (
            id INTEGER PRIMARY KEY,
            name VARCHAR(255),
            media_folder TEXT NOT NULL UNIQUE
        )
    `)
    db.close()
}

export default initDatabase