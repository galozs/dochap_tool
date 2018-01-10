import svgwrite
from dochap_tool.common_utils import utils
from svgwrite import cm, mm

colors = ['grey', 'black', 'orange', 'teal','green','blue','red','brown','pink','yellow']

def draw_test(w, h):
    dwg = svgwrite.Drawing(size=(100*cm, 10*cm), profile='tiny', debug=True)
    # set user coordinate space
    rect = dwg.rect(
        insert=(10*mm, 10*mm),
        size=(10*mm, 10*mm),
        fill='blue',
        stroke='red',
        opacity=0.5,
        stroke_width=1*mm
    )
    dwg.add(rect)
    return dwg.tostring()


def draw_transcripts(transcripts):
    """
    Draw multiple transcripts.
    @param transcripts (dict) of the form {t_id : [exons]}
    @return (list of string) list of svgs
    """
    if len(transcripts) == 0:
        return None
    starts = [transcript[0]['real_start'] for transcript in transcripts.values()]
    ends = [transcript[-1]['real_end'] for transcript in transcripts.values()]
    # probably need a check to see what strand it is.
    # there is a 'sign' value stored in every exon in the gtf files
    min_start = min(starts)
    max_end = max(ends)
    svgs = {}
    show_line_numbers = True
    for t_id, exons in transcripts.items():
        start_end_info = (min_start, max_end)
        svg = draw_exons_real(exons, t_id, start_end_info, show_line_numbers)
        svgs[t_id] = svg
        show_line_numbers = False
    return svgs



def draw_exons(exons, transcript_id):
    """Draw rectangles representing exons"""
    dwg = svgwrite.Drawing(size=(12*cm, 10*mm), profile='tiny', debug=True)
    if len(exons) == 0:
        return None
    squashed_start = exons[0]['relative_start']
    squashed_end = exons[-1]['relative_end']
    for exon in exons:
        rect = create_exon_rect(dwg, exon, squashed_start, squashed_end)
        dwg.add(rect)
    text = add_text(dwg, transcript_id)
    dwg.add(text)
    return dwg.tostring()


def draw_exons_real(exons, transcript_id, start_end_info = None, draw_line_numbers = True):
    """Draw rectangles representing exons real positions"""
    # draw line
    # on the line draw rectangles representing exons with introns spaces between them
    if len(exons) == 0:
        return None
    dwg = svgwrite.Drawing(size=(12*cm, 10*mm), profile='tiny', debug=True)

    if not start_end_info:
        transcript_start = exons[0]['real_start']
        transcript_end = exons[-1]['real_end']
    else:
        transcript_start = start_end_info[0]
        transcript_end = start_end_info[1]

    for exon in exons:
        rect = create_exon_rect_real_pos(dwg, exon, transcript_start, transcript_end)
        dwg.add(rect)
    add_line(dwg, transcript_start,transcript_end,draw_line_numbers)
    text = add_text(dwg, transcript_id)
    dwg.add(text)
    return dwg.tostring()


def draw_domains(domains, variant_index):
    """Draw rectangles representing domains"""
    dwg = svgwrite.Drawing(size=(10*cm, 10*mm), profile='tiny', debug=True)
    for domain in domains:
        rect = create_domain_rect(dwg, domain)
        dwg.add(rect)
    text = add_text(dwg, variant_index)
    dwg.add(text)
    return dwg.tostring()


def create_exon_rect_real_pos(dwg, exon, transcript_start, transcript_end):
    start = exon['real_start']
    normalized_start = utils.clamp_value(start, transcript_start, transcript_end) * 100
    end  = exon['real_end']
    normalized_end = utils.clamp_value(end, transcript_start, transcript_end) * 100
    normalized_length = abs(normalized_end - normalized_start)
    #c = colors[exon['index'] % len(colors)]
    c = colors[5]
    rect = dwg.rect(
        insert=(normalized_start * mm, 5 * mm),
        size=(normalized_length * mm, 5 * mm),
        fill=c,
        opacity=0.5
    )
    return rect


def create_exon_rect(dwg, exon, squashed_start, squashed_end):
    start = exon['relative_start']
    normalized_start = utils.clamp_value(start, squashed_start, squashed_end) * 100
    end = exon['relative_end']
    normalized_end = utils.clamp_value(end, squashed_start, squashed_end) * 100
    normalized_length = abs(normalized_start - normalized_end)
    c = colors[exon['index'] % len(colors)]
    rect = dwg.rect(
        insert=(normalized_start * mm, 5 * mm),
        size=(normalized_length * mm, 5 * mm),
        fill=c,
        opacity=0.5
    )
    return rect


def create_domain_rect(dwg, domain):
    start = domain['start']
    length = domain['end'] - domain['start']
    # TODO different colors
    c = colors[domain['index'] % len(colors)]
    rect = dwg.rect(
        insert=((start/50)*mm, 5*mm),
        size=((length/50)*mm, 5*mm),
        fill=c,
        opacity=0.5
    )
    return rect


def add_line(dwg, start_value, end_value, draw_line_numbers = True):
    normalized_start_position = (0*mm, 7.5*mm)
    normalized_end_position = (120*mm, 7.5*mm)
    dwg.add(dwg.line(start=normalized_start_position,end=normalized_end_position, stroke="green"))
    if draw_line_numbers:
        dwg.add(dwg.text(insert=(0*mm, 3*mm), text=str(start_value)))
        dwg.add(dwg.text(insert=(100*mm, 3*mm), text=str(end_value)))
    return None


def add_text(dwg, t):
    text = dwg.text(insert=(30*mm, 4.5*mm), text=t)
    return text
