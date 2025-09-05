#!/usr/bin/python3
"""
Module for converting Markdown files to HTML.
"""
import sys
import os
import re
import hashlib


def parse_bold_emphasis(text):
    """Parse bold and emphasis syntax in text."""
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'__(.+?)__', r'<em>\1</em>', text)
    return text


def parse_special_syntax(text):
    """Parse special syntax: [[]] for MD5 and (()) for character removal."""
    def md5_replace(match):
        content = match.group(1)
        md5_hash = hashlib.md5(content.encode()).hexdigest()
        return md5_hash
    
    def remove_c(match):
        content = match.group(1)
        content = re.sub(r'[cC]', '', content)
        return content
    
    text = re.sub(r'\[\[(.+?)\]\]', md5_replace, text)
    text = re.sub(r'\(\((.+?)\)\)', remove_c, text)
    return text


def process_line_formatting(text):
    """Process all inline formatting in a text."""
    text = parse_special_syntax(text)
    text = parse_bold_emphasis(text)
    return text


def markdown_to_html(input_file, output_file):
    """Convert Markdown file to HTML."""
    with open(input_file, 'r') as f:
        lines = f.readlines()
    
    html_lines = []
    i = 0
    
    while i < len(lines):
        line = lines[i].rstrip('\n')
        
        if line.startswith('#'):
            match = re.match(r'^(#{1,6})\s+(.+)$', line)
            if match:
                level = len(match.group(1))
                content = process_line_formatting(match.group(2))
                html_lines.append(f'<h{level}>{content}</h{level}>')
            i += 1
        
        elif line.startswith('- '):
            ul_items = []
            while i < len(lines) and lines[i].startswith('- '):
                item_content = process_line_formatting(lines[i][2:].rstrip('\n'))
                ul_items.append(f'<li>{item_content}</li>')
                i += 1
            if ul_items:
                html_lines.append('<ul>')
                html_lines.extend(ul_items)
                html_lines.append('</ul>')
        
        elif line.startswith('* '):
            ol_items = []
            while i < len(lines) and lines[i].startswith('* '):
                item_content = process_line_formatting(lines[i][2:].rstrip('\n'))
                ol_items.append(f'<li>{item_content}</li>')
                i += 1
            if ol_items:
                html_lines.append('<ol>')
                html_lines.extend(ol_items)
                html_lines.append('</ol>')
        
        elif line.strip():
            paragraph_lines = []
            while i < len(lines) and lines[i].strip() and not lines[i].startswith('#') and not lines[i].startswith('- ') and not lines[i].startswith('* '):
                paragraph_lines.append(lines[i].rstrip('\n'))
                i += 1
            
            if paragraph_lines:
                html_lines.append('<p>')
                for j, p_line in enumerate(paragraph_lines):
                    formatted_line = process_line_formatting(p_line)
                    if j < len(paragraph_lines) - 1:
                        html_lines.append(formatted_line)
                        html_lines.append('<br/>')
                    else:
                        html_lines.append(formatted_line)
                html_lines.append('</p>')
        else:
            i += 1
    
    with open(output_file, 'w') as f:
        f.write('\n'.join(html_lines) + '\n')


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print("Usage: ./markdown2html.py README.md README.html", file=sys.stderr)
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2]
    
    if not os.path.exists(input_file):
        print(f"Missing {input_file}", file=sys.stderr)
        sys.exit(1)
    
    markdown_to_html(input_file, output_file)
    sys.exit(0)