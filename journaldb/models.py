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
import datetime


from dbbase.core import DBBase
from journaldb.core import JournalEntry


def create_entry(db: DBBase, title: str, content: str, date: datetime.date, tags: str = ""):
    """
    Create a new journal entry.
    """
    JournalEntry.create(db, title=title, content=content, date=date, tags=tags)


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
