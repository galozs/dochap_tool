import svgwrite
import json
from dochap_tool.common_utils import utils
from svgwrite import cm, mm

colors = ['grey', 'black', 'orange', 'teal', 'green', 'blue', 'red', 'brown', 'pink', 'yellow']

TEXT_X = 121
TEXT_Y = 35
DRAWING_SIZE_X = 140
DRAWING_SIZE_Y = 40
EXON_START_X = 10
EXON_END_X = 110
EXON_Y = 32
LINE_START_X = 0
LINE_END_X = 120
LINE_Y = 34.5
EXON_HEIGHT = 5
LINE_ROWS_HALF_HEIGHT = 2
TOOLTIP_SIZE_X = 40
TOOLTIP_SIZE_Y = 30


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


def draw_combination(
        user_transcripts: dict,
        user_color: str,
        db_transcripts: dict,
        db_color: str
        ) -> tuple:
    """draw_combination

    :param user_transcripts:
    :type user_transcripts: dict
    :param user_color:
    :type user_color: str
    :param db_transcripts:
    :type db_transcripts: dict
    :param db_color:
    :type db_color: str
    :rtype: dict, dict, str
    """
    transcripts_lists = (user_transcripts, db_transcripts)
    min_starts = []
    max_ends = []
    for transcript_lists in transcripts_lists:
        starts = [transcript[0]['real_start'] for transcript in transcript_lists.values()]
        ends = [transcript[-1]['real_end'] for transcript in transcript_lists.values()]
        # probably need a check to see what strand it is.
        # there is a 'sign' value stored in every exon in the gtf files
        min_starts.append(min(starts))
        max_ends.append(max(ends))
    start_end_info = (min(min_starts), max(max_ends))
    user_svgs = draw_transcripts(user_transcripts, user_color, start_end_info, False)
    db_svgs = draw_transcripts(db_transcripts, db_color, start_end_info, False)
    dwg = svgwrite.Drawing(size=to_size((DRAWING_SIZE_X, DRAWING_SIZE_Y), mm), profile='tiny', debug=True)
    add_line(dwg, start_end_info[0], start_end_info[1], True, True)
    return user_svgs, db_svgs, dwg.tostring()



def draw_transcripts(
        transcripts: dict,
        exons_color:str = 'blue',
        start_end_info: tuple = None,
        numbered_line: bool = True
        ) -> list:
    """draw transcripts

    :param transcripts:
    :type transcripts: dict
    :param exons_color:
    :type exons_color: str
    :param start_end_info:
    :type start_end_info: tuple
    :param numbered_line:
    :type numbered_line: bool
    :rtype: list
    """
    if len(transcripts) == 0:
        return None
    if not start_end_info:
        starts = [transcript[0]['real_start'] for transcript in transcripts.values()]
        ends = [transcript[-1]['real_end'] for transcript in transcripts.values()]
        # probably need a check to see what strand it is.
        # there is a 'sign' value stored in every exon in the gtf files
        min_start = min(starts)
        max_end = max(ends)
    else:
        min_start = start_end_info[0]
        max_end = start_end_info[1]
    svgs = {}
    show_line_numbers = numbered_line
    for t_id, exons in transcripts.items():
        start_end_info = (min_start, max_end)
        svg = draw_exons_real(exons, t_id, start_end_info, show_line_numbers, exons_color)
        svgs[t_id] = svg
        show_line_numbers = False
    return svgs



def draw_exons(exons: list, transcript_id: str) -> str:
    """draw_exons

    :param exons:
    :type exons: list
    :param transcript_id:
    :type transcript_id: str
    :rtype: str
    """
    """Draw rectangles representing exons"""
    dwg = svgwrite.Drawing(size=to_size((DRAWING_SIZE_X, DRAWING_SIZE_Y),mm), profile='tiny', debug=True)
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


def draw_exons_real(
        exons: list,
        transcript_id: str,
        start_end_info: tuple = None,
        draw_line_numbers: bool = True,
        exons_color: str = 'blue'
        ) -> str:
    """draw exons genomic location on a line

    :param exons:
    :type exons: list
    :param transcript_id:
    :type transcript_id: str
    :param start_end_info:
    :type start_end_info: tuple
    :param draw_line_numbers:
    :type draw_line_numbers: bool
    :param exons_color:
    :type exons_color: str
    :rtype str:
    """
    # draw line
    # on the line draw rectangles representing exons with introns spaces between them
    if len(exons) == 0:
        return None
    dwg = svgwrite.Drawing(size=to_size((DRAWING_SIZE_X, DRAWING_SIZE_Y),mm), profile='tiny', debug=True)
    dwg.add_stylesheet('./dochap_tool/styles/my_style.css', title='interactive style')

    if not start_end_info:
        transcript_start = exons[0]['real_start']
        transcript_end = exons[-1]['real_end']
    else:
        transcript_start = start_end_info[0]
        transcript_end = start_end_info[1]

    add_line(dwg, transcript_start,transcript_end,draw_line_numbers)
    for exon in exons:
        exon_tooltip_group = create_exon_rect_real_pos(dwg, exon, transcript_start, transcript_end, exons_color)
        dwg.add(exon_tooltip_group)
    text_group = add_text(dwg, transcript_id, exons_color)
    dwg.add(text_group)
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


def create_exon_rect_real_pos(
        dwg: svgwrite.Drawing,
        exon: dict,
        transcript_start: int,
        transcript_end: int,
        color: str = 'blue'
        ) -> svgwrite.container.Group:
    """create_exon_rect_real_pos

    :param dwg:
    :type dwg: svgwrite.Drawing
    :param exon:
    :type exon: dict
    :param transcript_start:
    :type transcript_start: int
    :param transcript_end:
    :type transcript_end: int
    :param color:
    :type color: str
    :rtype: svgwrite.container.Group
    """
    start = exon['real_start']
    normalized_start = (utils.clamp_value(start, transcript_start, transcript_end) * 100) + EXON_START_X
    end  = exon['real_end']
    normalized_end = (utils.clamp_value(end, transcript_start, transcript_end) * 100) + EXON_START_X
    normalized_length = abs(normalized_end - normalized_start)
    #c = colors[exon['index'] % len(colors)]
    rect_insert = (normalized_start ,EXON_Y)
    rect_size = (normalized_length ,EXON_HEIGHT)
    rect = dwg.rect(
        insert = to_size(rect_insert, mm),
        size = to_size(rect_size, mm),
        fill = color,
        opacity = 0.5
    )
    #rect.set_desc(title="im a title", desc="im a desc")
    tooltip = add_tooltip(dwg, rect_insert, rect_size, exon, color)
    rect_tooltip_group = dwg.g(id_='exon')
    rect_tooltip_group.add(tooltip)
    rect_tooltip_group.add(rect)
    return rect_tooltip_group


def add_tooltip(
        dwg: svgwrite.Drawing,
        rect_insert: tuple,
        rect_size: tuple,
        tooltip_data: dict,
        background_color: str = None,
        text_color: str = None,
        params: list = None,
        ) -> svgwrite.container.Group:
    """add_tooltip

    :param dwg:
    :type dwg: svgwrite.Drawing
    :param rect_insert:
    :type rect_insert: tuple
    :param rect_size:
    :type rect_size: tuple
    :param tooltip_data:
    :type tooltip_data: dict
    :param background_color:
    :type background_color: str
    :param text_color:
    :type text_color: str
    :param params:
    :type params: list
    :rtype: svgwrite.container.Group
    """

    tooltip_group = dwg.g(class_="special_rect_tooltip")
    tooltip_size = (TOOLTIP_SIZE_X,TOOLTIP_SIZE_Y)
    tooltip_insert_x = min(max(rect_insert[0] + 0.5*rect_size[0] - (TOOLTIP_SIZE_X/2), 0), DRAWING_SIZE_X - tooltip_size[0])
    tooltip_insert = tooltip_insert_x, rect_insert[1] - TOOLTIP_SIZE_Y
    #TODO USE JAVASCRIPT TO SOLVE BOUNDING PROBLEM - east
    #OR THE DAMN <USE> THING
    background_rect = dwg.rect(
        insert = to_size(tooltip_insert, mm),
        size = to_size(tooltip_size, mm),
        rx = 2*mm,
        ry = 2*mm,
    )
    if background_color:
        background_rect.fill(background_color, opacity = 0.5)

    tooltip_group.add(background_rect)

    text = dwg.text(insert = to_size((tooltip_insert[0],tooltip_insert[1]-1),mm), text="")
    tooltip_data = extract_tooltip(tooltip_data, params)
    num_lines = len(tooltip_data)
    for index, (key, value) in enumerate(tooltip_data.items()):
        line = f'{key}: {value}'
        height = tooltip_size[1]/num_lines
        text.add(svgwrite.text.TSpan(
            text = line,
            x = [(tooltip_insert[0]+1)*mm],
            dy = [height*mm],
            text_anchor="start"
        ))
    tooltip_group.add(text)
    return tooltip_group


def extract_tooltip(exon: dict, params: list=None, name_dict: dict=None ) -> dict:
    """extract_tooltip

    :param exon:
    :type exon: dict
    :param params:
    :type params: list
    :param name_dict:
    :type name_dict: dict
    :rtype: dict
    """
    if not params:
        params = ['index', 'length', 'real_start', 'real_end', 'relative_start', 'relative_end']
    if not name_dict:
        name_dict= {'real_start':'genomic_start', 'real_end':'genomic_end' }
    extracted_params= {switch_names(key, name_dict):value for key,value in exon.items() if key in params}
    return extracted_params


def switch_names(key: str, name_dict: dict) -> str:
    """switch_names

    :param key:
    :type key: str
    :param name_dict:
    :type name_dict: dict
    :rtype: str
    """
    return name_dict.get(key, key).replace('_', ' ')


def create_exon_rect(dwg: svgwrite.Drawing, exon: dict, squashed_start: int, squashed_end: int) -> svgwrite.shapes.Rect:
    """create_exon_rect

    :param dwg:
    :type dwg: svgwrite.Drawing
    :param exon:
    :type exon: dict
    :param squashed_start:
    :type squashed_start: int
    :param squashed_end:
    :type squashed_end: int
    :rtype: svgwrite.shapes.Rect
    """
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


def create_domain_rect(dwg: svgwrite.Drawing, domain: dict) -> svgwrite.shapes.Rect:
    """create_domain_rect

    :param dwg:
    :type dwg: svgwrite.Drawing
    :param domain:
    :type domain: dict
    :rtype: svgwrite.shapes.Rect
    """
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


def add_line(
        dwg: svgwrite.Drawing,
        start_value: int,
        end_value: int,
        draw_line_numbers: bool = True,
        draw_line_rows: bool = False
        ) -> None:
    """add_line

    :param dwg:
    :type dwg: svgwrite.Drawing
    :param start_value:
    :type start_value: int
    :param end_value:
    :type end_value: int
    :param draw_line_numbers :True:
    :type draw_line_numbers: bool
    :param draw_line_rows :False:
    :type draw_line_rows: bool
    :rtype: svgwrite.shapes.Line
    """
    start = [LINE_START_X, LINE_Y]
    end = [LINE_END_X, LINE_Y]
    sign_start = [EXON_START_X, LINE_Y]
    sign_end = [EXON_END_X, LINE_Y]
    normalized_start_position = to_size(start,mm)
    normalized_end_position = to_size(end, mm)
    line = dwg.add(dwg.line(start=normalized_start_position,end=normalized_end_position, stroke="green"))
    if draw_line_numbers:
        dwg.add(dwg.text(
            insert=to_size((sign_start[0] - 10, LINE_Y - 3), mm),
            text=str(start_value)
        ))
        dwg.add(dwg.text(
            insert=to_size((sign_end[0] - 10, LINE_Y - 3),mm),
            text=str(end_value)
        ))
    if draw_line_rows:
        start_line_start = sign_start[:]
        start_line_end = sign_start[:]
        start_line_start[1] -= LINE_ROWS_HALF_HEIGHT
        start_line_end[1] += LINE_ROWS_HALF_HEIGHT
        start_line_start = to_size(start_line_start, mm)
        start_line_end = to_size(start_line_end, mm)
        end_line_start = sign_end[:]
        end_line_end = sign_end[:]
        end_line_start[1] -= LINE_ROWS_HALF_HEIGHT
        end_line_end[1] += LINE_ROWS_HALF_HEIGHT
        end_line_start = to_size(end_line_start, mm)
        end_line_end = to_size(end_line_end, mm)
        # add the lines
        dwg.add(dwg.line(start=start_line_start, end=start_line_end,stroke="red"))
        dwg.add(dwg.line(start=end_line_start, end=end_line_end,stroke="red"))

    return None


def to_size(tup: tuple, size: svgwrite.Unit) -> tuple:
    """to_size

    :param tup:
    :type tup: tuple
    :param size:
    :type size: svgwrite.Unit
    :rtype: tuple
    """
    new_tup = tuple([t*size for t in tup])
    return new_tup

def add_text(dwg: svgwrite.Drawing, t: str, background_color: str = 'teal') -> svgwrite.container.Group:
    """add_text

    :param dwg:
    :type dwg: svgwrite.Drawing
    :param t:
    :type t: str
    :param background_color:
    :type background_color: str
    :rtype: svgwrite.container.Group
    """
    transcript_name_group = dwg.g(class_ = 'transcript_id_rect')
    rect_insert = (TEXT_X, TEXT_Y - EXON_HEIGHT)
    rect_size = (DRAWING_SIZE_X - TEXT_X, EXON_HEIGHT*2)
    rect = dwg.rect(
            insert=to_size(rect_insert,mm),
            size = to_size(rect_size, mm),
            fill = background_color,
            opacity = 0.2
    )
    text = dwg.text(insert=(TEXT_X*mm, TEXT_Y*mm), text=t)
    transcript_name_group.add(rect)
    transcript_name_group.add(text)
    tooltip_group = add_tooltip(
            dwg,
            rect_insert,
            rect_size,
            {'t_id':t},
            background_color,
            params=['t_id']
    )

    transcript_name_group.add(tooltip_group)
    return transcript_name_group
