import sqlite3

def init_db():
    conn = sqlite3.connect("clan_bot.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS members (
            tag TEXT PRIMARY KEY,
            name TEXT,
            role TEXT
        )
    """)
    conn.commit()
    conn.close()

def sync_members(current_members):
    conn = sqlite3.connect("clan_bot.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT tag, name FROM members")
    db_members = {row[0]: row[1] for row in cursor.fetchall()}
    
    current_tags = {m['tag']: m['name'] for m in current_members}
    
    joined = [name for tag, name in current_tags.items() if tag not in db_members]
    left = [name for tag, name in db_members.items() if tag not in current_tags]
    
    cursor.execute("DELETE FROM members")
    for tag, name in current_tags.items():
        role = next((m['role'] for m in current_members if m['tag'] == tag), 'member')
        cursor.execute("INSERT INTO members (tag, name, role) VALUES (?, ?, ?)", (tag, name, role))
        
    conn.commit()
    conn.close()
    
    return joined, left
