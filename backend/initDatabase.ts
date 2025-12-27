import { DatabaseSync } from 'node:sqlite'

const initDatabase = (db: DatabaseSync) => {
    db.open()
    db.exec(`
        CREATE TABLE IF NOT EXISTS settings (
            key TEXT NOT NULL UNIQUE,
            value TEXT,
            format TEXT NOT NULL
        )
    `)
    if(db.prepare(`SELECT * FROM settings WHERE key = 'MOVIE_LOCATION'`).all().length === 0) {
        db.exec(`
            INSERT INTO settings
            ( key, value, format )
            VALUES
            ( 'MOVIE_LOCATION', '', 'folder' )
        `)
    }
    
    db.exec(`
        CREATE TABLE IF NOT EXISTS movies (
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
        CREATE TABLE IF NOT EXISTS libraries (
            id INTEGER PRIMARY KEY,
            name VARCHAR(255),
            media_folder TEXT NOT NULL UNIQUE
        )
    `)
    db.exec(`
        CREATE TABLE IF NOT EXISTS collections (
            id INTEGER PRIMARY KEY,
            title VARCHAR(255),
            thumbnail_file_name TEXT,
            library_id INTEGER
        )
    `)
    db.exec(`
        CREATE TABLE IF NOT EXISTS movies__collections (
            id INTEGER PRIMARY KEY,
            movie_id INTEGER NOT NULL,
            collection_id INTEGER NOT NULL
        )    
    `)
    db.close()
}

export default initDatabase