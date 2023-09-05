#!/usr/bin/env python3
import os
import sys
import signal
import argparse
from datetime import datetime

APP_DESC = 'A tool to help me create or modify my blog.'


def new_post(title, tags, category, date):
    if date is None:
        date = datetime.now().strftime('%Y-%m-%d')
    mardown_template = f'''---
title: {title}
tags: {tags}
category: {category}
date: {date}
---
'''
    # convert title to lowercase and replace space with dash
    title = title.lower().replace(' ', '-')
    markdown_path = f'./content/post/{date}-{title}.md'
    with open(markdown_path, 'w') as f:
        f.write(mardown_template)


def list_posts():
    for root, dirs, files in os.walk('./content/post/'):
        for file in files:
            if not file.endswith('.md'):
                continue
            path = os.path.join(root, file)
            with open(path, 'r') as f:
                for line in f.readlines():
                    if line.startswith('title:'):
                        print(line[6:].strip())
                        break


def update_post(path, title, tags, category, date):
    with open(path, 'r') as f:
        lines = f.readlines()

    for line in lines:
        if line.startswith('title:'):
            if title is not None:
                lines[lines.index(line)] = f'title: {title}\n'
        elif line.startswith('tags:'):
            if tags is not None:
                lines[lines.index(line)] = f'tags: {tags}\n'

        elif line.startswith('category:'):
            if category is not None:
                lines[lines.index(line)] = f'category: {category}\n'

        elif line.startswith('date:'):
            if date is None:
                date = datetime.now().strftime('%Y-%m-%d')
            lines[lines.index(line)] = f'date: {date}\n'

    with open(path, 'w') as f:
        f.writelines(lines)


def main(args):
    parser = argparse.ArgumentParser(description=APP_DESC)
    subparsers = parser.add_subparsers(help='sub commands', dest='command')

    # new
    new_parser = subparsers.add_parser('new', help='create a new post')
    new_parser.add_argument('title', help='title of the post')
    new_parser.add_argument('-t', '--tags', nargs='+', help='tags of the post')
    new_parser.add_argument('-c', '--category', help='category of the post')
    new_parser.add_argument('-d', '--date', help='date of the post')

    # list
    list_parser = subparsers.add_parser('list', help='list all posts')

    # update
    update_parser = subparsers.add_parser('update', help='update a post')
    update_parser.add_argument('path', help='path of the post')
    update_parser.add_argument('--title', help='title of the post')
    update_parser.add_argument(
        '-t', '--tags', nargs='+', help='tags of the post')
    update_parser.add_argument('-c', '--category', help='category of the post')
    update_parser.add_argument('-d', '--date', help='date of the post')

    args = parser.parse_args(args)
    if args.command is None:
        parser.print_help()
        return
    if args.command == 'new':
        new_post(args.title, args.tags, args.category, args.date)

    elif args.command == 'list':
        list_posts()

    elif args.command == 'update':
        update_post(args.path, args.title, args.tags, args.category, args.date)


def signal_handler(sig, frame):
    sys.exit(0)


if __name__ == '__main__':
    signal.signal(signal.SIGINT, signal_handler)
    main(sys.argv[1:])
