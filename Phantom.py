#!/usr/bin/env python3
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
    'uni': re.compile(b'\033\[[\d;]*m'),  # Universal color code
    'fg': re.compile(b'(?<!\d)3\d'),      # Foreground color
    'bg': re.compile(b'(?<!\d)4\d'),      # Background color
    'ul': re.compile(b'[\[;m]4[\[;m]'),   # Underline
    'hl': re.compile(b'[\[;m]1[\[;m]'),   # Highlight
    'dk': re.compile(b'[\[;m]0[\[;m]')}   # Darken


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
    if b'\033[m' == text:
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
        css_class += lookup[int(fgcolor.group(0))]
    # Dealing with underline
    if pattern['ul'].search(text):
        css_class += 'ul '
    # Dealing with background color
    bgcolor = pattern['bg'].search(text)
    if bgcolor:
        css_class += lookup[int(bgcolor.group(0))]
    return '<span class="{0}">'.format(css_class)


def html_converter(linein):
    output = linein.replace(' ', '&nbsp;')
    return output


BODY = ""
parser = argparse.ArgumentParser(description=
                                 'Phantom of 35.10, BBS -> HTML converter')
parser.add_argument('FN', metavar="filename", help="input file name")
parser.add_argument('-p', '--print', action='store_true', dest='prt',
                    help="Print to the screen as well")
args = parser.parse_args()
fn = args.FN
with open(fn, 'rb') as fh:
    content = fh.readlines()

# Get rid of the runaway char here:
with open('tmp.html', 'w') as fh:
    for line in content:
        try:
            # Try to convert big5 encoded line first
            # It will be treated as byte string if it can't be translated
            line = line.decode('big5')
        except UnicodeDecodeError:
            result = set(pattern['uni'].findall(line))
            if result:
                for patt in result:
                    code = ctranslator(patt).encode('big5')
                    line = line.replace(patt, code)
            import pdb;pdb.set_trace()
            # First attempt to decode colorized line
            try:
                line = line.decode('big5')
            except UnicodeDecodeError:
                # There is expected to be a runaway \xa1 in the signature
                # Two-colored word shall trigger this exception too
                # FIXME: ungly hack
                if b'\xa1<span class="c40">\xb4' in line:
                    line = line.replace(b'\xa1<span class="c40">\xb4', b'\xa1\xb4')
                if b'<span class="c30">\xa1<span class="c46">? <' in line:
                    # FIXME: dual color case
                    line = line.replace(b'<span class="c30">\xa1<span class="c46">? <',
                                        b'<span class="c30"><span class="c46">? <')
                if b'<span class="c30">\xa2<span class="c37">\xa8' in line:
                    # FIXME: dual color case
                    line = line.replace(b'<span class="c30">\xa2<span class="c37">\xa8',
                                        b'<span class="c37">\xa2\xa8')
                if b'<span class="c30c40">\xa2<span class="c37">\xab\xa2<span class="c30">\xaa\xa2<span class="c37c47">\xaa' in line:
                    # FIXME: dual color case
                    line = line.replace(b'<span class="c30c40">\xa2<span class="c37">\xab', b'<span class="c30c40">\xa2\xab<span class="c37">')
                if b'<span class="c37">\xa2<span class="c30">\xaa' in line:
                    # FIXME: dual color issue
                    line = line.replace(b'<span class="c37">\xa2<span class="c30">\xaa', b'<span class="c37">\xa2\xaa<span class="c30">')
                if b'<span class="c30">\xa2<span class="c37c47">\xaa' in line:
                    # FIXME: dual color issue
                    line = line.replace(b'<span class="c30">\xa2<span class="c37c47">\xaa', b'<span class="c30">\xa2\xaa<span class="c37c47">')

            line = line.decode('big5')

        if args.prt:
            print(line)
        BODY += html_converter(line[:len(line)-1]) + '<br>'
    fh.write(HEADER)
    fh.write(BODY)
    fh.write(FOOTER)

print("JOB CMPL, tmp.html saved")
