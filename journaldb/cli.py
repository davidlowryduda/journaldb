"""
cli.py

# **********************************************************************
#       This is cli.py, part of journaldb
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
import argparse
import os


from journaldb.core import JournalEntry, init_journal_db
from journaldb.models import search_entries
from journaldb.pageio import (
    JournalEntryData,
    parse_file,
    add_data_to_db,
    update_data_in_db,
    write_data_to_file,
    write_template_file,
)


def get_db_path(dbdir, dbname):
    """
    Construct the full path to the database file based on the directory and
    file name.
    """
    return os.path.join(dbdir, dbname)


def add_command(db, ix, filename):
    jed = parse_file(filename)
    add_data_to_db(db, ix, jed)


def update_command(db, ix, filename):
    jed = parse_file(filename)
    update_data_in_db(db, ix, jed)


def show_command(db, entry_id):
    entry = JournalEntry.objects(db).get(id=entry_id)
    if not entry:
        raise ValueError(f"Entry {entry_id} not in database")
    print(f"Title: {entry['title']}\nDate: {entry['date']}\nTags: {entry['tags']}\n\nContent:\n{entry['content']}")


def list_show_command(db):
    entries = JournalEntry.all(db)
    for entry in entries:
        print(f"Id: {entry['id']} | Title: {entry['title']} | Date: {entry['date']}")


def write_command(db, entry_id, filename=None):
    entry = JournalEntry.objects(db).get(id=entry_id)
    if not entry:
        raise ValueError(f"Entry {entry_id} not in database")
    filename = filename if filename else 'entry.txt'
    write_data_to_file(entry, filename)


def template_command(filename=None):
    filename = filename if filename else 'entry.txt'
    if os.path.exists(filename):
        raise FileExistsError(f"The file '{filename}' already exists.")
    write_template_file(filename)


def search_command(db, ix, query_str, full=False):
    results = search_entries(ix, query_str)
    if not results:
        print("No results found.")
        return
    for result, score in results:
        if full:
            print(f"ID: {result['id']}\nTitle: {result['title']}\nDate: {result['date']}\nTags: {result['tags']}\n\nContent:\n{result['content']}\n")
        else:
            print(f"ID: {result['id']} | Title: {result['title']} | Score : {score}")


def make_parser():
    parser = argparse.ArgumentParser(
        description="JournalDB Command Line Interface. See help for individual commands",
        epilog="Made by David Lowry-Duda <david@lowryduda.com>."
    )

    # Global options for database directory and file name
    parser.add_argument('--dbdir', default='.', help='Directory where the database is stored (default: current directory)')
    parser.add_argument('--dbname', default='journal.db', help='Database file name (default: journal.db)')

    subparsers = parser.add_subparsers(dest='command', required=True)

    parser_add = subparsers.add_parser('add', help='Add a new journal entry from a file')
    parser_add.add_argument('filename', help='The file to add to the database')

    parser_update = subparsers.add_parser('update', help='Update a journal entry from a file')
    parser_update.add_argument('filename', help='The file to update in the database')

    parser_show = subparsers.add_parser('show', help='Show a journal entry by ID')
    parser_show.add_argument('id', type=int, nargs='?', default=0, help='The ID of the journal entry to show')
    parser_show.add_argument('--list', action='store_true', help='Show all entries')

    parser_write = subparsers.add_parser('write', help='Write a journal entry to a file')
    parser_write.add_argument('id', type=int, help='The ID of the journal entry to write to a file')
    parser_write.add_argument('filename', nargs='?', default=None, help='The file to write to (defaults to entry.txt)')

    parser_template = subparsers.add_parser('template', help='Create a template file')
    parser_template.add_argument('filename', nargs='?', default=None, help='The file to write the template to (defaults to entry.txt)')

    parser_search = subparsers.add_parser('search', help='Search journal entries')
    parser_search.add_argument('query_str', help='The search query')
    parser_search.add_argument('--full', action='store_true', help='Show full entry information')

    return parser


def main():
    parser = make_parser()
    args = parser.parse_args()
    db_path = get_db_path(args.dbdir, args.dbname)
    db, ix = init_journal_db(
        db_path, os.path.join(args.dbdir, "searchindex")
    )

    if args.command == 'add':
        add_command(db, ix, args.filename)
    elif args.command == 'update':
        update_command(db, ix, args.filename)
    elif args.command == 'show':
        if args.list:
            list_show_command(db)
        else:
            if args.id == 0:
                raise ValueError(f"Entry 0 doesn't exist. Please provide valid entry id.")
            show_command(db, args.id)
    elif args.command == 'write':
        write_command(db, args.id, args.filename)
    elif args.command == 'template':
        template_command(args.filename)
    elif args.command == 'search':
        search_command(db, ix, args.query_str, full=args.full)


if __name__ == "__main__":
    main()
