import svgwrite
from svgwrite import cm, mm


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


def draw_exons(exons, transcript_id):
    """Draw rectangles representing exons"""
    dwg = svgwrite.Drawing(size=(10*cm, 10*mm), profile='tiny', debug=True)
    for exon in exons:
        rect = create_exon_rect(dwg, exon)
        dwg.add(rect)
    text = add_text(dwg, transcript_id)
    dwg.add(text)
    return dwg.tostring()


def draw_exons_real(exons, transcript_id):
    """Draw rectangles representing exons real positions"""
    dwg = svgwrite.Drawing(size=(10*cm, 10*mm), profile='tiny', debug=True)
    for exon in exons:
        rect = create_exon_rect(dwg, exon, real_start=True)
        dwg.add(rect)
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


def create_exon_rect(dwg, exon, real_start=False):
    start = exon['real_start'] if real_start else exon['relative_start']
    length = exon['length']
    color = ['blue', 'green', 'yellow', 'red']
    c = color[exon['index'] % 4]
    rect = dwg.rect(
        insert=((start/50)*mm, 5*mm),
        size=((length/50)*mm, 5*mm),
        fill=c,
        opacity=0.5
    )
    return rect


def create_domain_rect(dwg, domain):
    start = domain['start']
    length = domain['end'] - domain['start']
    # TODO different colors
    color = ['grey', 'black', 'orange', 'teal']
    c = color[domain['index'] % 4]
    rect = dwg.rect(
        insert=((start/50)*mm, 5*mm),
        size=((length/50)*mm, 5*mm),
        fill=c,
        opacity=0.5
    )
    return rect


def add_text(dwg, t):
    text = dwg.text(insert=(5*mm, 4.5*mm), text=t)
    return text
