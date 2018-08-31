import re
import click
from bs4 import BeautifulSoup


Small = {
    'zero': 0,
    'one': 1,
    'two': 2,
    'three': 3,
    'four': 4,
    'five': 5,
    'six': 6,
    'seven': 7,
    'eight': 8,
    'nine': 9,
    'ten': 10,
    'eleven': 11,
    'twelve': 12,
    'thirteen': 13,
    'fourteen': 14,
    'fifteen': 15,
    'sixteen': 16,
    'seventeen': 17,
    'eighteen': 18,
    'nineteen': 19,
    'twenty': 20,
    'thirty': 30,
    'forty': 40,
    'fifty': 50,
    'sixty': 60,
    'seventy': 70,
    'eighty': 80,
    'ninety': 90
}

Magnitude = {
    'thousand':     1000,
    'million':      1000000,
    'billion':      1000000000,
    'trillion':     1000000000000,
    'quadrillion':  1000000000000000,
    'quintillion':  1000000000000000000,
    'sextillion':   1000000000000000000000,
    'septillion':   1000000000000000000000000,
    'octillion':    1000000000000000000000000000,
    'nonillion':    1000000000000000000000000000000,
    'decillion':    1000000000000000000000000000000000,
}


class NumberException(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)


def text2num(s):
    a = re.split(r"[\s-]+", s)
    n = 0
    g = 0
    for w in a:
        x = Small.get(w, None)
        if x is not None:
            g += x
        elif w == "hundred" and g != 0:
            g *= 100
        else:
            x = Magnitude.get(w, None)
            if x is not None:
                n += g * x
                g = 0
            else:
                raise NumberException("Unknown number: "+w)
    return n + g






@click.command()
@click.argument('file_name')
@click.argument('player')
def parse_file(file_name, player):
    """
    Parse a TAZ transcript from http://tazscripts.tumblr.com/tazscripts to extract lines where 
    a dice roll was likely reported for a given character.
    """
    soup = BeautifulSoup(open(file_name), 'html.parser')

    all_spans = soup.find_all('span')
    for span in all_spans:
        if span.text is not None and player == span.text.replace(':', '').strip():
            player_p_class = span.parent['class'][0]
            break
    
    player_dialog = soup.find_all('p', attrs={'class': player_p_class}) 

    lines_of_dialog = []

    for c in player_dialog:
        if c.span.string is None or c.span.string.replace(':', "").strip() != player: 
            continue

        line_of_dialog = u""
        for cc in c.span.next_siblings:
            for ch in cc.children:
                if ch.string is None:
                    continue
                line_of_dialog += ch.string

        tokens = line_of_dialog.split()
        new_tokens = []
        for token in tokens:
            try:
                new_token = unicode(text2num(token.lower().replace('.', '').replace(',','').strip()))
            except NumberException:
                new_token = token
            new_tokens.append(new_token)
        line_of_dialog = u' '.join(new_tokens)

        if bool(re.search(r'\d', line_of_dialog)):
            lines_of_dialog.append(line_of_dialog)

    for lod in lines_of_dialog:
        print u"{:}".format(lod)
        print ""

'''
<p class="c2">
    <span class="c1">
     Travis:
    </span>
    <span class="c0">
     [
    </span>
    <span class="c0 c4">
     Laughing
    </span>
    <span class="c3 c0">
     ] You take 10 psychic damage.
    </span>
   </p>
'''

if __name__ == '__main__':
    parse_file()
