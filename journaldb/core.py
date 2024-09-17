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


from dbbase.core import DBBase
from dbbase.models import Model, TextField, DateField


class JournalEntry(Model):
    table_name = "journal_entries"

    title = TextField(nullable=False)
    content = TextField(nullable=False)
    date = DateField()
    tags = TextField()  # Stored internally as json

    def __str__(self):
        return f"<JournalEntry(title={self.title}, date={self.date}, tags={self.tags}, content_start={self.content[:50]})>"


def init_journal_db(db_path: str):
    db = DBBase(db_path)
    db.connect()
    JournalEntry.create_table(db)
    return db
