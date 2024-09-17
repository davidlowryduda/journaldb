"""
core.py - db interaction

# **********************************************************************
#       This is core.py, part of journaldb.
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
import json
import os


from whoosh import index
from whoosh.fields import Schema, TEXT, ID, DATETIME


from dbbase.core import DBBase
from dbbase.models import Model, IntegerField, TextField, TimestampField
from dbbase.query import QueryableModel


class JournalEntry(Model, QueryableModel):
    table_name = "journal_entries"

    id = IntegerField(primary_key=True)
    title = TextField(nullable=False)
    content = TextField(nullable=False)
    date = TimestampField(nullable=False)
    tags = TextField()  # Stored internally as json

    def __str__(self):
        return f"<JournalEntry(id={self.id}, title={self.title}, date={self.date}, tags={self.tags}, content_start={self.content[:50]})>"


def init_journal_db(db_path: str, index_dir="indexdir"):
    db = DBBase(db_path)
    db.connect()
    JournalEntry.create_table(db)
    ix = init_whoosh_index(index_dir)
    return db, ix


def create_whoosh_schema():
    """
    Define the Whoosh schema for journal entries.
    """
    return Schema(
        id=ID(stored=True, unique=True),  # Unique ID for the journal entry
        title=TEXT(stored=True),
        content=TEXT(stored=True),
        date=DATETIME(stored=True),
        tags=TEXT(stored=True)
    )


def init_whoosh_index(index_dir="indexdir"):
    """
    Initialize or open the Whoosh index.
    """
    if not os.path.exists(index_dir):
        os.mkdir(index_dir)
    if index.exists_in(index_dir):
        ix = index.open_dir(index_dir)
    else:
        schema = create_whoosh_schema()
        ix = index.create_in(index_dir, schema)
    return ix
