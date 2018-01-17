import svgwrite
from dochap_tool.common_utils import utils
from dochap_tool.compare_utils import compare_exons
from svgwrite import cm, mm
from typing import Union

colors = ['grey', 'black', 'orange', 'teal', 'green', 'blue', 'red', 'brown', 'pink', 'yellow']

MATCH_X = 5
MATCH_Y = 5
MATCH_SIZE_X = 15
MATCH_SIZE_Y = 10
TEXT_X = 115
TEXT_Y = 35
DRAWING_SIZE_X = 140
DRAWING_SIZE_Y = 40
EXON_START_X = 10
EXON_END_X = 110
EXON_Y = 30
LINE_START_X = 0
LINE_END_X = 115
LINE_Y = 34.5
EXON_HEIGHT = 8
LINE_ARCHES_HALF_HEIGHT = 2
TOOLTIP_SIZE_X = 40
TOOLTIP_SIZE_Y = 28
TEXT_X_OFFSET = 10
px_to_mm = 3.779528
transform_px_to_mm = f'scale({px_to_mm})'

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
        gene_name: str,
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
    matching_dict = compare_exons.compare_user_db_transcripts(user_transcripts, db_transcripts)
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
    user_svgs = draw_transcripts(user_transcripts, user_color, start_end_info, False, matching_dict)
    db_svgs = draw_transcripts(db_transcripts, db_color, start_end_info, False)
    view_box_string = f'0 0 {DRAWING_SIZE_X} {DRAWING_SIZE_Y}'
    dwg = svgwrite.Drawing(size=to_size((DRAWING_SIZE_X, DRAWING_SIZE_Y), mm), profile='tiny', debug=True) #,viewBox=view_box_string)
    line_group = add_line(dwg, start_end_info[0], start_end_info[1], True, True, num_arches=0)
    dwg.add(line_group)
    dwg.add(add_text(dwg, '', tooltip_data = {'gene symbol':gene_name}))
    dwg.defs.add(dwg.script(content='fix_all();'))
    return user_svgs, db_svgs, dwg.tostring()



def draw_transcripts(
        transcripts: dict,
        exons_color:str = 'blue',
        start_end_info: tuple = None,
        numbered_line: bool = True,
        matching_dict: dict = None,
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
    :param matching_dict:
    :type matching_dict: dict
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
        svg = draw_exons_real(exons, t_id, start_end_info, show_line_numbers, exons_color, matching_dict)
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
    text = add_text(dwg, transcript_id, tooltip_data= {'Transcript id':transcript_id})
    dwg.add(text)
    dwg.defs.add(dwg.script(content='fix_all();'))
    return dwg.tostring()


def draw_exons_real(
        exons: list,
        transcript_id: str,
        start_end_info: tuple = None,
        draw_line_numbers: bool = True,
        exons_color: str = 'blue',
        matching_dict: dict = {},
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
    :param matching_dict:
    :type matching_dict: dict
    :rtype str:
    """
    view_box_string = f'0 0 {DRAWING_SIZE_X} {DRAWING_SIZE_Y}'
    dwg = svgwrite.Drawing(size=to_size((DRAWING_SIZE_X, DRAWING_SIZE_Y),mm), profile='tiny', debug=True)#, viewBox = view_box_string)
    if len(exons) == 0:
        return dwg.tostring()
    # TODO probably not working right now
    #dwg.add_stylesheet('./dochap_tool/styles/my_style.css')
    dwg.defs.add(dwg.script(content='fix_all();'))

    if not start_end_info:
        transcript_start = exons[0]['real_start']
        transcript_end = exons[-1]['real_end']
    else:
        transcript_start = start_end_info[0]
        transcript_end = start_end_info[1]

    line_group = add_line(dwg, transcript_start,transcript_end,draw_line_numbers)
    dwg.add(line_group)
    for exon in exons:
        exon_tooltip_group = create_exon_rect_real_pos(dwg, exon, transcript_start, transcript_end,len(exons), exons_color)
        dwg.add(exon_tooltip_group)
        text_group = add_text(dwg, transcript_id, exons_color, tooltip_data={'Transcript id': transcript_id} )
    dwg.add(text_group)
    if matching_dict:
        matching_text = 'Match exists' if transcript_id in matching_dict else 'No Match'
        color = 'green' if transcript_id in matching_dict else 'red'
        tooltip_data = {'Match':matching_dict.get(transcript_id,'no match')}
        match_group = add_matching_status(dwg, matching_text, color, tooltip_data)
        dwg.add(match_group)
    return dwg.tostring()


def draw_domains(domains, variant_index):
    """Draw rectangles representing domains"""
    dwg = svgwrite.Drawing(size=(10*cm, 10*mm), profile='tiny', debug=True)
    for domain in domains:
        rect = create_domain_rect(dwg, domain)
        dwg.add(rect)
    text = add_text(dwg, variant_index, tooltip_data={'domain variant': variant_index})
    dwg.add(text)
    return dwg.tostring()


def create_exon_rect_real_pos(
        dwg: svgwrite.Drawing,
        exon: dict,
        transcript_start: int,
        transcript_end: int,
        num_exons:int,
        color: str = 'blue',
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
    # check if before cds start
    exon_cds_intersection = utils.get_exon_cds_intersection(exon)
    if exon_cds_intersection is not None:
        normalized_intersection_x2 = (utils.clamp_value(exon_cds_intersection[1], transcript_start, transcript_end) * 100) + EXON_START_X

        first_start = (rect_insert[0], LINE_Y - (rect_size[1]/6))
        first_size = (normalized_intersection_x2 - rect_insert[0],rect_size[1] /3)
        second_start = (first_start[0]+first_size[0], rect_insert[1])
        second_size = (rect_insert[0]+rect_size[0] - second_start[0], rect_size[1])

        exon_group = dwg.g(class_ = 'exon_group')
        rect1 = dwg.rect(
                insert = to_size(first_start, mm),
                size = to_size(first_size, mm),
                fill = color,
                opacity = 0.5
                )
        rect2 = dwg.rect(
                insert = to_size(second_start, mm),
                size = to_size(second_size, mm),
                fill = color,
                opacity = 0.5
                )
        exon_group.add(rect1)
        exon_group.add(rect2)
        rect = exon_group
    else:
        rect = dwg.rect(
            insert = to_size(rect_insert, mm),
            size = to_size(rect_size, mm),
            fill = color,
            opacity = 0.5
        )
    tooltip_data = {}
    tooltip_data['Exon number'] = f"{exon['index']+1}/{num_exons}"
    if 'cds_start' in exon and 'cds_end' in exon:
        tooltip_data['CDS location'] = f"{exon['cds_start']} - {exon['cds_end']}"
    tooltip_data['Genomic location'] = f"{exon['real_start']} - {exon['real_end']}"
    tooltip_data['Relative location'] = f"{exon['relative_start']} - {exon['relative_end']}"
    tooltip_data['Length'] = F"{exon['length']}"
    tooltip = add_tooltip(dwg, rect_insert, rect_size, tooltip_data, background_color='#d3d3d3', text_color='#00008b', border_color=color)
    rect_tooltip_group = dwg.g(class_='exon')
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
        border_color: str = None,
        params: list = None,
        under: bool = False
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
    :param under:
    :type under: bool
    :rtype: svgwrite.container.Group
    """
    tooltip_group = dwg.g(class_="special_rect_tooltip")
    tooltip_size = (TOOLTIP_SIZE_X, TOOLTIP_SIZE_Y if not under else TOOLTIP_SIZE_Y/2)
    tooltip_insert_x = max(rect_insert[0] + 0.5*rect_size[0] - (TOOLTIP_SIZE_X/2), 0)
    tooltip_insert_x = min(tooltip_insert_x, DRAWING_SIZE_X - 1.3*tooltip_size[0])
    tooltip_insert_y = rect_insert[1] if under else rect_insert[1] - TOOLTIP_SIZE_Y
    tooltip_insert = tooltip_insert_x, tooltip_insert_y
    background_rect = dwg.rect(
        insert = to_size(tooltip_insert, mm),
        size = to_size(tooltip_size, mm),
        rx = 2*mm,
        ry = 2*mm,
        fill=background_color,
        opacity = 1.0,
        stroke=border_color
    )
    tooltip_group.add(background_rect)
    text = dwg.text(insert = to_size((tooltip_insert[0],tooltip_insert[1]-2),mm), text="")
    tooltip_data = extract_tooltip(tooltip_data, params)
    num_lines = len(tooltip_data)
    for index, (key, value) in enumerate(tooltip_data.items()):
        line = f'{key}: {value}'
        height = tooltip_size[1]/num_lines
        text.add(svgwrite.text.TSpan(
            text = line,
            x = [(tooltip_insert[0]+1)*mm],
            dy = [height*mm],
            text_anchor="start",
            style=f"fill:{text_color};"
        ))
    tooltip_group.add(text)
    return tooltip_group


def extract_tooltip(tooltip_data: dict, params: list=None, name_dict: dict=None ) -> dict:
    """extract_tooltip

    :param tooltip_data:
    :type tooltip_data: dict
    :param params:
    :type params: list
    :param name_dict:
    :type name_dict: dict
    :rtype: dict
    """
    if not params:
        params = tooltip_data.keys()
    if not name_dict:
        name_dict= {'real_start':'genomic_start', 'real_end':'genomic_end' }
    extracted_params= {switch_names(key, name_dict):value for key,value in tooltip_data.items() if key in params}
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
        draw_line_arches: bool = True,
        num_arches: int = 10,
        arch_stroke_color: str = 'black',
        arch_tooltip: bool = False
        ) -> svgwrite.container.Group:
    """add_line

    :param dwg:
    :type dwg: svgwrite.Drawing
    :param start_value:
    :type start_value: int
    :param end_value:
    :type end_value: int
    :param draw_line_numbers :True:
    :type draw_line_numbers: bool
    :param draw_line_arches :True:
    :type draw_line_arches bool
    :param num_arches :10:
    :type num_arches: int
    :param arch_stroke_color :red:
    :type arch_stroke_color: str
    :param arch_tooltip :False:
    :type arch_tooltip: bool
    :rtype: svgwrite.container.Group
    """
    start = [LINE_START_X, LINE_Y]
    end = [LINE_END_X, LINE_Y]
    sign_start = [EXON_START_X, LINE_Y]
    sign_end = [EXON_END_X, LINE_Y]
    normalized_start_position = to_size(start,mm)
    normalized_end_position = to_size(end, mm)
    line_group = dwg.g(class_ = 'line_group')
    line_group.add(dwg.line(start=normalized_start_position,end=normalized_end_position, stroke="green"))
    if draw_line_numbers:
        line_group.add(dwg.text(
            insert=to_size((sign_start[0] - TEXT_X_OFFSET, LINE_Y - 3), mm),
            text=str(start_value)
        ))
        line_group.add(dwg.text(
            insert=to_size((sign_end[0] - TEXT_X_OFFSET, LINE_Y - 3),mm),
            text=str(end_value)
        ))

    num_arches = max(2, num_arches)
    if draw_line_arches:
        space_between_arches = (sign_end[0] - sign_start[0])/num_arches
        for i in range(num_arches+1):
            arch_position_x = sign_start[0] + (i * space_between_arches)
            arch_position_y = LINE_Y
            arch_start = (arch_position_x, arch_position_y - LINE_ARCHES_HALF_HEIGHT)
            arch_end = (arch_position_x, arch_position_y + LINE_ARCHES_HALF_HEIGHT)
            line_group.add(dwg.line(
                start=to_size(arch_start, mm),
                end=to_size(arch_end, mm),
                stroke=arch_stroke_color
            ))
            if arch_tooltip:
                pass
    return line_group



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

def add_text(
        dwg: svgwrite.Drawing,
        text_string: str,
        color: str = 'teal',
        tooltip_data:dict = None
        ) -> svgwrite.container.Group:
    """add_text

    :param dwg:
    :type dwg: svgwrite.Drawing
    :param text_string:
    :type text_string: str
    :param color:
    :type color: str
    :rtype: svgwrite.container.Group
    """
    transcript_name_group = dwg.g(class_ = 'transcript_id_rect')
    rect_insert = (TEXT_X, TEXT_Y - EXON_HEIGHT)
    rect_size = (DRAWING_SIZE_X - TEXT_X, EXON_HEIGHT*2)
    rect = dwg.rect(
            insert=to_size(rect_insert,mm),
            size = to_size(rect_size, mm),
            fill = color,
            opacity = 0.2
    )
    text = dwg.text(insert=(TEXT_X*mm, TEXT_Y*mm), text=text_string)
    transcript_name_group.add(text)
    transcript_name_group.add(rect)
    tooltip_group = add_tooltip(
            dwg,
            rect_insert,
            rect_size,
            tooltip_data,
            background_color='#d3d3d3',
            text_color='#00008b',
            border_color=color
    )

    transcript_name_group.add(tooltip_group)
    return transcript_name_group

def add_matching_status(
        dwg: svgwrite.Drawing,
        text_string: str,
        color: str = 'teal',
        tooltip_data:dict = None,
        ) -> svgwrite.container.Group:
    """add_matching_status

    :param dwg:
    :type dwg: svgwrite.Drawing
    :param text_string:
    :type text_string: str
    :param color:
    :type color: str
    :param tooltip_data:
    :type tooltip_data: dict
    :rtype: svgwrite.container.Group
    """
    match_status_group = dwg.g(class_ = 'match_status_group')
    rect_insert = (MATCH_X, MATCH_Y)
    rect_size = (MATCH_SIZE_X, MATCH_SIZE_Y)
    rect = dwg.rect(
            insert=to_size(rect_insert,mm),
            size = to_size(rect_size, mm),
            fill = color,
            opacity = 0.2
    )
    text = dwg.text(insert=to_size(rect_insert,mm), text=text_string)
    match_status_group.add(text)
    match_status_group.add(rect)
    tooltip_group = add_tooltip(
            dwg,
            rect_insert,
            rect_size,
            tooltip_data,
            background_color='#d3d3d3',
            text_color='#00008b',
            border_color=color,
            under = True
    )
    some_y = (LINE_Y - MATCH_SIZE_Y - MATCH_Y) / 2
    middle_match_status = (MATCH_Y + MATCH_SIZE_Y )/ 2
    path_group = dwg.g(class_ = 'path_group', transform = transform_px_to_mm)
    path_string = f'M {LINE_START_X} {LINE_Y} L {LINE_START_X} {some_y} L {MATCH_X} {some_y} L {MATCH_X} {middle_match_status}'
    path_group.add(dwg.path(d = path_string, opacity = 0.5, stroke = color))
    # add path line from begining of the transcript line to the status match
    match_status_group.add(path_group)
    match_status_group.add(tooltip_group)
    return match_status_group
