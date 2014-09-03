#!/usr/bin/env python
''' Phantom of 35.10, BBS -> HTML converter, in honor of ATMBBS
    140.115.35.10, BBS for bone-ash people
           This program is distributed under GNU GPLv2.
    Source https://github.com/Cypresslin/PhantomOf3510      '''
import argparse
import re

# Color code reference
lookup = {30: 'c30',
          31: 'c31',
          32: 'c32',
          33: 'c33',
          34: 'c34',
          35: 'c35',
          36: 'c36',
          37: 'c37',
          40: 'c40',
          41: 'c41',
          42: 'c42',
          43: 'c43',
          44: 'c44',
          45: 'c45',
          46: 'c46',
          47: 'c47',
          90: 'c90',
          91: 'c91',
          92: 'c92',
          93: 'c93',
          94: 'c94',
          95: 'c95',
          96: 'c96',
          97: 'c97'}


# pattern for regex, defined here to avoid re-compiling waste
pattern = {
    'uni': re.compile('\033\[[\d;]*m'),  # Universal color code
    'fg': re.compile('(?<!\d)3\d'),      # Foreground color
    'bg': re.compile('(?<!\d)4\d'),      # Background color
    'ul': re.compile('[\[;m]4[\[;m]'),   # Underline
    'hl': re.compile('[\[;m]1[\[;m]'),   # Highlight
    'dk': re.compile('[\[;m]0[\[;m]')}   # Darken


HEADER = """
<!DOCTYPE html>
<html>
  <head>
    <link rel="stylesheet" type="text/css" href="Style.css">
    <meta charset="utf-8">
  </head>
  <body class="content" onload="setInterval('blinkIt()',500)">
  <script type="text/javascript">
  function blinkIt() {
    if (!document.all) return;
    else {
    for(i=0;i<document.all.tags('blink').length;i++){
      s=document.all.tags('blink')[i];
      s.style.visibility=(s.style.visibility=='visible')?'hidden':'visible';
      }
    }
  }
  </script>
"""


FOOTER = """
  <blink> TEST </blink>
  </body>
</html>
"""


def ctranslator(text):
    '''  activate translation'''
    # *[m close it
    if '\033[m' == text:
        return '</span>'
    css_class = ""
    # Dealing with foreground color
    fgcolor = pattern['fg'].search(text)
    # highlight symbol possibility: [1m  [1; ;1;  [;1m
    if pattern['hl'].search(text):
        if fgcolor:  # highlight color
            css_class += lookup[int(fgcolor.group(0)) + 60]
        else:        # highlight only
            css_class += 'c1'
    elif pattern['dk'].search(text) and not fgcolor: # darken only
        css_class += 'c30'
    elif fgcolor:  # not highlighted
        css_class += lookup[fgcolor]
    # Dealing with underline
    if pattern['ul'].search(text):
        css_class += 'ul '
    # Dealing with background color
    bgcolor = pattern['bg'].search(text)
    if bgcolor:
        css_class += lookup[int(bgcolor.group(0))]
    return '<span class="{0}">'.format(css_class)


HTML = ""
parser = argparse.ArgumentParser(description=
                                 'Phantom of 35.10, BBS -> HTML converter')
parser.add_argument('FN', metavar="filename", help="input file name")
parser.add_argument('-p', '--print', action='store_true', dest='prt',
                    help="Print to the screen as well")
args = parser.parse_args()
fn = args.FN
with open(fn, 'r') as fh:
    content = fh.readlines()

with open('tmp.html', 'w') as fh:
    for line in content:
        line = line.decode("big5").encode("UTF-8")
        if args.prt:
            print line
        line = line.replace(" ", "&nbsp;")
        result = pattern['uni'].findall(line)
        if result:
            for patt in result:
                code = ctranslator(patt)
                line = line.replace(patt, code)
        HTML += line[:len(line)-1] + '<br>\n'
    fh.write(HEADER)
    fh.write(HTML)
    fh.write(FOOTER)

print "JOB CMPL, tmp.html saved"
