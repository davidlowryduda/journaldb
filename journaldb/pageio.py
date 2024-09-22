"""
pageio.py - writing to and reading from plaintext files

# **********************************************************************
#       This is pageio.py, part of journaldb
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
import yaml
from dataclasses import dataclass
from datetime import datetime


from journaldb.models import create_entry


@dataclass
class JournalEntryData:
    title: str
    tags: str
    content: str
    date: datetime
    id: int = 0


def parse_file(filename: str) -> JournalEntryData:
    with open(filename, 'r') as file:
        content = file.read()
        if '---' in content:
            header, body = content.split('---', 1)[1].split('---', 1)
        else:
            raise ValueError("File format incorrect. YAML header not found.")
        header_data = yaml.safe_load(header)
        if not all(k in header_data for k in ['title', 'tags', 'date']):
            raise ValueError("YAML header must contain 'title', 'tags', and 'date'.")
        date_obj = datetime.strptime(header_data['date'], '%Y-%m-%d')
        return JournalEntryData(
            title=header_data['title'],
            tags=header_data['tags'],
            content=body.strip(),
            date=date_obj,
            id=header_data.get('id', 0)
        )


def add_data_to_db(db, ix, jed: JournalEntryData):
    """
    Add a JournalEntryData instance to the database.
    """
    create_entry(
        db=db,
        ix=ix,
        title=jed.title,
        content=jed.content,
        date=jed.date,
        tags=jed.tags
    )


def update_data_in_db(db, ix, jed: JournalEntryData):
    """
    Update an entry in the database.
    """
    if jed.id == 0:
        raise ValueError("Invalid entry ID")
    update_entry(
        db=db,
        ix=ix,
        entry_id=jed.id,
        title=jed.title,
        content=jed.content,
        date=jed.date,
        tags=tags_str
    )


def write_data_to_file(jed: JournalEntryData, fname: str):
    """
    Write a JournalEntryData instance to a file with a YAML header.
    """
    yaml_header = {
        'title': jed.title,
        'tags': jed.tags,
        'date': jed.date.strftime('%Y-%m-%d'),
        'id': jed.id
    }
    with open(fname, 'w') as file:
        file.write('---\n')
        yaml.dump({k: v for k, v in yaml_header.items() if v is not None},
                  file, default_flow_style=False)
        file.write('---\n\n')
        file.write(jed.content)


def write_template_file(fname: str, entryid: int = 0):
    """
    Write a template file.
    """
    jed = JournalEntryData(
        title="post title",
        tags='+tag1, +tag2',
        content="Write stuff here.",
        date=datetime.today(),
        id=entryid
    )
    write_data_to_file(jed, fname)
