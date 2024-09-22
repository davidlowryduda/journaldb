"""
models.py - db ORM

# **********************************************************************
#       This is models.py, part of journaldb.
#       Copyright (c) 2024 David Lowry-Duda <david@lowryduda.com>
#       All Rights Reserved.
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see
#                 <http://www.gnu.org/licenses/>.
# **********************************************************************
"""
from datetime import datetime


from whoosh.qparser import MultifieldParser


from dbbase.core import DBBase
from journaldb.core import JournalEntry


def add_entry_to_index(ix, entry_id, title, content, date, tags):
    """
    Add or update a journal entry in the Whoosh index.
    """
    writer = ix.writer()
    writer.add_document(
        id=str(entry_id),
        title=title,
        content=content,
        date=date,
        tags=tags
    )
    writer.commit()


def create_entry(db: DBBase, ix, title: str, content: str, date: datetime, tags: str = ""):
    """
    Create a new journal entry and index it with Whoosh.
    """
    # Insert the entry into the SQLite database
    JournalEntry.create(db, title=title, content=content, date=date, tags=tags)

    # Get the entry ID and index the entry
    # I assume title+date are unique.
    entry = JournalEntry.get(db, title=title, date=date)
    add_entry_to_index(ix, entry['id'], title, content, date, tags)


def update_entry_in_index(ix, entry_id, title, content, date, tags):
    """
    Update a journal entry in the Whoosh index.
    """
    writer = ix.writer()
    writer.update_document(
        id=str(entry_id),
        title=title,
        content=content,
        date=date,
        tags=tags
    )
    writer.commit()


def update_entry(db: DBBase, ix, entry_id, title: str = None,
                 content: str = None, date: datetime = None, tags: str = None):
    """
    Update a journal entry in the database and Whoosh index. The update is
    based on the `entry_id`.
    """
    # Retrieve the current entry from the database
    entry = JournalEntry.get(db, id=entry_id)
    if not entry:
        print("Entry not found!")
        return

    # Update the entry with the provided data
    updated_fields = {}
    if title:
        updated_fields['title'] = title
    if content:
        updated_fields['content'] = content
    if date:
        updated_fields['date'] = date
    if tags:
        updated_fields['tags'] = tags

    # Update the database
    JournalEntry.update(db, where={'id': entry_id}, updates=updated_fields)

    # Update the Whoosh index
    updated_entry = JournalEntry.get(db, id=entry_id)
    update_entry_in_index(ix, entry_id, updated_entry['title'], updated_entry['content'], updated_entry['date'], updated_entry['tags'])
    print(f"Journal entry with ID {entry_id} has been updated.")


def delete_entry_from_index(ix, entry_id):
    """
    Remove a journal entry from the Whoosh index.
    """
    writer = ix.writer()
    writer.delete_by_term('id', str(entry_id))
    writer.commit()


def delete_entry(db: DBBase, ix, entry_id: int):
    """
    Delete a journal entry from the database and Whoosh index.

    :param entry_id: The ID of the journal entry to delete.
    """
    # Retrieve the current entry from the database
    entry = JournalEntry.get(db, id=entry_id)
    if not entry:
        print("Entry not found!")
        return

    # Delete the entry from the database
    JournalEntry.delete(db, id=entry_id)

    # Delete the entry from the Whoosh index
    delete_entry_from_index(ix, entry_id)
    print(f"Journal entry with ID {entry_id} has been deleted.")


def search_entries(ix, query_str):
    """
    Search journal entries in the Whoosh index.

    :param ix: Whoosh index
    :param query_str: Search query
    :return: List of matching entries
    """
    with ix.searcher() as searcher:
        query = MultifieldParser(["title", "content", "tags"], schema=ix.schema).parse(query_str)
        results = searcher.search(query)
        ret = [(dict(result.items()), result.score) for result in results]
        return ret


def get_all_entries(db: DBBase):
    """
    Retrieve all journal entries.
    """
    return JournalEntry.all(db)


def search_entries_by_title(db: DBBase, title: str):
    """
    Search journal entries by title.
    """
    return JournalEntry.objects(db).filter(title=title).all()


def search_entries_by_title_like(db: DBBase, title: str):
    """
    Search journal entries by title, imprecisely.
    """
    return JournalEntry.objects(db).filter_like(title=title).all()


def search_entries_by_tag_like(db: DBBase, tag: str):
    """
    Search journal entries by tag, imprecisely.
    """
    return JournalEntry.objects(db).filter_like(tags=tag).all()
