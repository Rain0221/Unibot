import os
import sys
import re
from PIL import Image, ImageDraw, ImageFont

'''
MIT License

Copyright (c) 2018 yp05327

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
'''

#####  define  #####
version = '0.0.2'
alpha = 125
note_image_width = 35
note_image_height = 18
fix_note_image_width = 2
note_width = note_image_width + fix_note_image_width
delta_unit_width = 120
image_left_right = 60
image_top_bottom = 60
unit_width = note_width * 12
unit_height = int(note_image_height * (64 + 48))
music_info_key_word = {
    'bpm': '#BPM01: (\d*)',
}

#####  read file  ######
def read_file(file_name):
    file_object = open(file_name, 'r')

    music_info = {}
    music_score = []

    read_step = 0
    try:
        for line in file_object:
            if read_step == 0:
                # get music info
                for key_word in music_info_key_word:
                    info = re.match(music_info_key_word[key_word], line)
                    if info:
                        music_info[key_word] = info.group(1)

            # get music score
            if line == '#MEASUREHS 00\n':
                read_step += 1
                continue

            if read_step == 1:
                info = re.match('#(\d\d\d)(\d)([0-9a-f]):(\w*)', line)

                if info:
                    music_score.append({
                        'unitid': info.group(1),
                        'type': info.group(2),
                        'row': info.group(3),
                        'list': info.group(4),
                    })
                    continue

                info = re.match('#(\d\d\d)(\d)([0-9a-f])(\d):(\w*)', line)
                if info:
                    music_score.append({
                        'unitid': info.group(1),
                        'type': info.group(2),
                        'row': info.group(3),
                        'longid': info.group(4),
                        'list': info.group(5),
                    })
                    continue

    finally:
        for key_word in music_info_key_word:
            if key_word not in music_info:
                music_info[key_word] = 'No info'

        file_object.close()

    music_score.sort(key=lambda x: x['unitid'])

    return music_info, music_score

def sus2img(musicid, diffculty):
    susfile = rf'data\assets\sekai\assetbundle\resources\startapp\music\music_score\{str(musicid).zfill(4)}_01\{diffculty}'
    music_info, music_score = read_file(susfile)
    score_image = create_image(music_info, music_score)
    print('music information:\nBPM:%s' % (music_info['bpm']))
    score_image = score_image.convert('RGB')
    score_image = score_image.resize((int(score_image.size[0]/4), int(score_image.size[1]/4)))
    dirs = rf'charts/sus/{musicid}'
    if not os.path.exists(dirs):
        os.makedirs(dirs)
    score_image.save(f'{dirs}/{diffculty}.png')



#####  create score image  ######
def create_image(music_info, music_score):
    # type 1
    note_info = {
        1: 'normal',
        2: 'crtcl',
        3: 'long_among',
        4: 'skill',
    }
    # type 5 1 flick up 2 long among unvisible 3 flick left 4 flick right 5,6 long start
    # type 3 1 long start 2 long end 3 long among 5 long among unvisible
    #####  read resource  #####
    note_normal = Image.open("pics/notes/notes_normal.png")
    note_crtcl = Image.open("pics/notes/notes_crtcl.png")
    note_long = Image.open("pics/notes/notes_long.png")
    note_long_among = Image.open("pics/notes/notes_long_among.png")
    note_long_among_crtcl = Image.open("pics/notes/notes_long_among_crtcl.png")
    note_long_among_unvisible = Image.open("pics/notes/note_long_among_unvisible.png")
    note_long_among_unvisible_crtcl = Image.open("pics/notes/note_long_among_unvisible_crtcl.png")
    note_flick = Image.open("pics/notes/notes_flick.png")
    note_flick_arrow = {
        1: [],
        3: [],
        4: []
    }
    note_flick_arrow_crtcl = {
        1: [],
        3: [],
        4: []
    }
    for i in range(1, 7):
        note_flick_arrow[1].append(Image.open("pics/notes/notes_flick_arrow_%02d.png" % i))
        note_flick_arrow[3].append(Image.open("pics/notes/notes_flick_arrow_%02d_diagonal.png" % i))
        note_flick_arrow[4].append(
            Image.open("pics/notes/notes_flick_arrow_%02d_diagonal.png" % i).transpose(Image.FLIP_LEFT_RIGHT))
        note_flick_arrow_crtcl[1].append(Image.open("pics/notes/notes_flick_arrow_crtcl_%02d.png" % i))
        note_flick_arrow_crtcl[3].append(Image.open("pics/notes/notes_flick_arrow_crtcl_%02d_diagonal.png" % i))
        note_flick_arrow_crtcl[4].append(
            Image.open("pics/notes/notes_flick_arrow_crtcl_%02d_diagonal.png" % i).transpose(Image.FLIP_LEFT_RIGHT))

    total_unit = int(music_score[-1]['unitid'])
    music_info['combo'] = 0

    # create image
    image_width = (int(total_unit / 4) + 1) * (unit_width + delta_unit_width)
    image_height = 4 * unit_height + image_top_bottom * 2
    music_score_image = Image.new('RGB', (image_width, image_height), (0, 0, 0, 100))

    # draw score lines
    draw = ImageDraw.Draw(music_score_image, 'RGBA')
    font = ImageFont.truetype(font="arial.ttf", size=50)
    big_line_list = []
    for i in range((int(total_unit / 4) + 1) * 2):
        x = image_left_right + i * (unit_width + delta_unit_width)
        # top left
        big_line_list.append((x, -10))
        # bottom left
        big_line_list.append((x, image_height + 10))
        # bottom right
        big_line_list.append((x + unit_width, image_height + 10))
        # top right
        big_line_list.append((x + unit_width, -10))

        for j in range(5):
            small_line_list = []
            # small line i top
            small_line_list.append((x + (j + 1) * note_width * 2, -10))
            # small line i bottom
            small_line_list.append((x + (j + 1) * note_width * 2, image_height + 10))
            draw.line(small_line_list, fill=(255, 255, 255), width=1)

    draw.line(big_line_list, fill=(137, 207, 240), width=5)

    # drow unit lines and text
    for i in range(total_unit + 2):
        x = image_left_right + int(i / 4) * (unit_width + delta_unit_width)
        y = image_height - (i % 4) * unit_height - image_top_bottom
        line_list = [(x, y), (x + unit_width, y)]
        draw.line(line_list, fill=(255, 255, 255), width=2)
        line_list = [(x, y - unit_height), (x + unit_width, y - unit_height)]
        draw.line(line_list, fill=(255, 255, 255), width=2)

        text_size = font.getsize(str(i))
        draw.text((x - text_size[0] - 5, y - 16), str(i), font=font, fill=(255, 255, 255))

        if i % 4 == 0:
            draw.text((x - text_size[0] - unit_width - delta_unit_width - 5, image_top_bottom - 16), str(i), font=font, fill=(255, 255, 255))

    polygon_list = {
        0: [],
        1: [],
        'result': [0, 0]
    }

    last_unitid = 0

    # draw notes
    notes_info_list = {
        'normal': {},
        'flick': {},
        'long': {},
        'long_among': {},
        'long_among_unvisible': {},
    }
    long_tmp_info = {
        0: {},
        1: {},
    }
    for u in range(len(music_score) + 1):
        if u != len(music_score):
            unitid = int(music_score[u]['unitid'])
            score_note_type = int(music_score[u]['type'])
            row = int(music_score[u]['row'], 16)
            list = re.findall('.{2}', music_score[u]['list'])

        if unitid == 0:
            last_unitid = unitid

        if last_unitid != unitid or u == len(music_score):
            # draw combo
            if u == len(music_score):
                tempunitid = unitid + 1
            else:
                tempunitid = unitid

            '''
            x = image_left_right + int(tempunitid / 4) * (unit_width + delta_unit_width)
            y = image_height - (tempunitid % 4) * unit_height - image_top_bottom

            text_size = font.getsize(str(music_info['combo']))
            draw.text((x - text_size[0] - 5, y + 16), str(music_info['combo']), font=font, fill=(255, 255, 255))

            if tempunitid % 4 == 0:
                text_size = font.getsize(str(music_info['combo']))
                draw.text((x - text_size[0] - unit_width - delta_unit_width - 5, image_top_bottom + 16), str(music_info['combo']), font=font, fill=(255, 255, 255))
            '''

            for long_id in [0, 1]:
                while polygon_list['result'][long_id] > 0:
                    # sort polygon list
                    polygon_list[long_id].sort(key=lambda x: x['unitid'] * 10000 + x['row_location'])

                    polygon_note_list = polygon_list[long_id]
                    if polygon_note_list[0]['image'] == note_crtcl:
                        color = (255, 241, 0, alpha)
                    else:
                        color = (60, 210, 160, alpha)

                    # draw polygon
                    while len(polygon_list[long_id]) > 1:
                        start_note = polygon_note_list[0]
                        end_note = polygon_note_list[1]

                        # check new row
                        if start_note['location'][1] > end_note['location'][1]:
                            # check new unit first
                            if start_note['row_location'] == 0 and start_note['unitid'] % 4 == 0:
                                slide_list = [
                                    (start_note['location'][0] - unit_width - delta_unit_width + fix_note_image_width,
                                     image_height - start_note['location'][1]),
                                    (end_note['location'][0] - unit_width - delta_unit_width + fix_note_image_width,
                                     end_note['location'][1] - image_height + image_top_bottom * 2),
                                    (end_note['location'][0] + end_note['size'][0] - unit_width - delta_unit_width - fix_note_image_width,
                                     end_note['location'][1] - image_height + image_top_bottom * 2),
                                    (start_note['location'][0] + start_note['size'][0] - unit_width - delta_unit_width - fix_note_image_width,
                                     image_height - start_note['location'][1])
                                ]
                                draw.polygon(slide_list, fill=color)

                                # polygon_paste_list.append([note_long, (start_note[0] - unit_width - delta_unit_width, image_height - start_note[1] - int(note_image_height / 2)), note_long])

                            # not new row
                            slide_list = [
                                (start_note['location'][0] + fix_note_image_width, start_note['location'][1] + int(start_note['size'][1] / 2)),
                                (end_note['location'][0] + fix_note_image_width, end_note['location'][1] + int(end_note['size'][1] / 2)),
                                (end_note['location'][0] + end_note['size'][0] - fix_note_image_width, end_note['location'][1] + int(end_note['size'][1] / 2)),
                                (start_note['location'][0] + start_note['size'][0] - fix_note_image_width, start_note['location'][1] + int(start_note['size'][1] / 2))
                            ]
                        else:
                            # draw bottom
                            slide_list = [
                                (start_note['location'][0] + unit_width + delta_unit_width + fix_note_image_width,
                                 image_height + start_note['location'][1] - image_top_bottom * 2 + int(start_note['size'][1] / 2)),
                                (end_note['location'][0] + fix_note_image_width,
                                 end_note['location'][1] + int(end_note['size'][1] / 2)),
                                (end_note['location'][0] + end_note['size'][0] - fix_note_image_width,
                                 end_note['location'][1] + int(end_note['size'][1] / 2)),
                                (start_note['location'][0] + start_note['size'][0] + unit_width + delta_unit_width - fix_note_image_width,
                                 image_height + start_note['location'][1] - image_top_bottom * 2 + int(start_note['size'][1] / 2))
                            ]
                            draw.polygon(slide_list, fill=color)

                            # polygon_paste_list.append([note_long, (end_note[0] - unit_width - delta_unit_width, image_top_bottom * 2 - image_height + end_note[1] - int(note_image_height / 2)), note_long])

                            # new row
                            slide_list = [
                                (start_note['location'][0] + fix_note_image_width,
                                 start_note['location'][1] + int(start_note['size'][1] / 2)),
                                (end_note['location'][0] - unit_width - delta_unit_width + fix_note_image_width,
                                 image_top_bottom * 2 - image_height + end_note['location'][1] + int(end_note['size'][1] / 2)),
                                (end_note['location'][0] + end_note['size'][0] - unit_width - delta_unit_width - fix_note_image_width,
                                 image_top_bottom * 2 - image_height + end_note['location'][1] + int(end_note['size'][1] / 2)),
                                (start_note['location'][0] + start_note['size'][0] - fix_note_image_width, start_note['location'][1] + int(start_note['size'][1] / 2))
                            ]

                        draw.polygon(slide_list, fill=color)

                        del polygon_list[long_id][0]

                        # check end
                        if 'end' in end_note:
                            break

                    # clear polygon list
                    polygon_list['result'][long_id] -= 1
                    del polygon_list[long_id][0]

        if u == len(music_score):
            break

        if score_note_type == 1:
            note_in_unit_location_index = -1

            for i in range(len(list)):
                note = list[i]
                note_type = int(note[0], 16)
                note_length = int(note[1], 16)

                note_in_unit_location_index += 1
                if note_type == 0 and note_length == 0:
                    continue
                elif note_type in note_info:
                    music_info['combo'] += 1

                    # get paste point
                    unit_location = (image_left_right + int(unitid / 4) * (unit_width + delta_unit_width), image_height - unitid % 4 * unit_height - image_top_bottom)

                    x, y, note_in_unit_location = get_location(note_length, unit_location, note_in_unit_location_index, row, len(list))

                    # get paste image and paste mask
                    if note_info[note_type] == 'normal':
                        paste_type = 'normal'
                        paste_image = note_normal
                    elif note_info[note_type] == 'crtcl':
                        paste_type = 'normal'
                        paste_image = note_crtcl
                    elif note_info[note_type] == 'long_among':
                        paste_type = 'long_among'
                        paste_image = note_long_among
                    elif note_info[note_type] == 'skill':
                        x = image_left_right + int(tempunitid / 4) * (unit_width + delta_unit_width)
                        y = image_height - (tempunitid % 4) * unit_height - image_top_bottom
                        draw.text((x - font.getsize('Skill')[0] - 5, y - 62), 'Skill', font=font, fill=(255, 255, 255))

                        if tempunitid % 4 == 0:
                            draw.text((x - font.getsize('Skill')[0] - unit_width - delta_unit_width - 5, image_top_bottom - 48), 'Skill', font=font, fill=(255, 255, 255))
                        continue
                    else:
                        print(note_info[note_type] + 'is not support (score_note_type = 1)')
                        continue

                    # paste note image
                    if paste_image:
                        note_image_localtion = (x, y)
                        # check new row
                        note_image_localtion2 = None
                        if unitid % 4 == 0 and note_in_unit_location_index == 0:
                            note_image_localtion2 = (x - unit_width - delta_unit_width, image_height - y - note_image_height)

                        notes_info_list[paste_type]['%d_%d_%d' % (unitid, row, note_in_unit_location)] = {
                            'image': paste_image,
                            'size': ((note_image_width + fix_note_image_width * 2) * note_length, note_image_height),
                            'length': note_length,
                            'location': note_image_localtion,
                            'location2': note_image_localtion2,
                            'unitid': unitid,
                            'row': row,
                            'row_location': note_in_unit_location,
                        }
        elif score_note_type == 5:
            # special note change
            # 1 flick
            # 5 long

            note_in_unit_location_index = -1

            for i in range(len(list)):
                special_note = list[i]
                special_note_type = int(special_note[0], 16)
                special_note_length = int(special_note[1], 16)

                note_in_unit_location_index += 1
                if special_note_type == 0 and special_note_length == 0:
                    continue

                # get paste point
                unit_location = (image_left_right + int(unitid / 4) * (unit_width + delta_unit_width), image_height - unitid % 4 * unit_height - image_top_bottom)
                x, y, note_in_unit_location = get_location(special_note_length, unit_location, note_in_unit_location_index, row, len(list))

                id = '%d_%d_%d' % (unitid, row, note_in_unit_location)
                if id not in notes_info_list['normal']:
                    note_image_localtion = (x, y)
                    # check new row
                    note_image_localtion2 = None
                    if unitid % 4 == 0 and note_in_unit_location_index == 0:
                        note_image_localtion2 = (x - unit_width - delta_unit_width, image_height - y - note_image_height)

                    notes_info_list['normal'][id] = {
                        'image': note_normal,
                        'size': ((note_image_width + fix_note_image_width * 2) * special_note_length, note_image_height),
                        'length': special_note_length,
                        'location': note_image_localtion,
                        'location2': note_image_localtion2,
                        'unitid': unitid,
                        'row': row,
                        'row_location': note_in_unit_location,
                    }

                note = notes_info_list['normal'][id]

                if special_note_type in [1, 3, 4]:
                    # flick 3 left 4 right
                    if note['image'] == note_crtcl:
                        paste_image = note['image']
                    else:
                        paste_image = note_flick

                    notes_info_list['flick'][id] = {
                        'image': paste_image,
                        'arrowtype': special_note_type,
                        'size': ((note_image_width + fix_note_image_width * 2) * special_note_length, note_image_height),
                        'length': special_note_length,
                        'location': note['location'],
                        'location2': note['location2'],
                        'unitid': unitid,
                        'row': row,
                        'row_location': note_in_unit_location,
                    }
                elif special_note_type == 2:
                    # unvisible long among
                    # unknow paste image type now defined in score_note_type 3 note_type 5
                    paste_image = note_long_among_unvisible

                    notes_info_list['long_among_unvisible'][id] = {
                        'image': paste_image,
                        'size': ((note_image_width + fix_note_image_width * 2) * special_note_length, note_image_height),
                        'length': special_note_length,
                        'location': note['location'],
                        'location2': note['location2'],
                        'unitid': unitid,
                        'row': row,
                        'row_location': note_in_unit_location,
                    }
                elif special_note_type == 5 or special_note_type == 6:
                    # long
                    if note['image'] == note_crtcl:
                        paste_image = note['image']
                    else:
                        paste_image = note_long

                    notes_info_list['long'][id] = {
                        'image': paste_image,
                        'size': ((note_image_width + fix_note_image_width * 2) * special_note_length, note_image_height),
                        'location': note['location'],
                        'location2': note['location2'],
                        'unitid': unitid,
                        'row': row,
                        'row_location': note_in_unit_location,
                    }
                elif special_note_type == 6:
                    # unkonw
                    pass
                else:
                    print(str(special_note_type) + 'is not support (score_note_type = 5)')
                    break
                del notes_info_list['normal'][id]
                continue
        elif score_note_type == 3:
            # long note info
            # 1 start 2 end 5 unvisible 3 among
            long_id = int(music_score[u]['longid'], 16)

            note_in_unit_location_index = -1

            for i in range(len(list)):
                long_note = list[i]
                long_note_type = int(long_note[0], 16)
                long_note_length = int(long_note[1], 16)

                note_in_unit_location_index += 1

                if long_note_type == 0 and long_note_length == 0:
                    continue

                # get paste point
                unit_location = (image_left_right + int(unitid / 4) * (unit_width + delta_unit_width), image_height - unitid % 4 * unit_height - image_top_bottom)
                x, y, note_in_unit_location = get_location(long_note_length, unit_location, note_in_unit_location_index, row, len(list))
                note_image_localtion = (x, y)

                # check new row
                note_image_localtion2 = None
                if unitid % 4 == 0 and note_in_unit_location_index == 0:
                    note_image_localtion2 = (x - unit_width - delta_unit_width, image_height - y - note_image_height)

                id = '%d_%d_%d' % (unitid, row, note_in_unit_location)
                if long_note_type == 1:
                    paste_image = note_long
                    if id in notes_info_list['long_among_unvisible']:
                        paste_image = long_tmp_info[long_id]['image']
                        notes_info_list['long'][id] = {
                            'image': paste_image,
                            'size': ((note_image_width + fix_note_image_width * 2) * long_note_length, note_image_height),
                            'location': note_image_localtion,
                            'location2': note_image_localtion2,
                            'unitid': unitid,
                            'row': row,
                            'row_location': note_in_unit_location,
                        }
                        del notes_info_list['long_among_unvisible'][id]
                    elif id in notes_info_list['long']:
                        paste_image = notes_info_list['long'][id]['image']
                    elif id in notes_info_list['normal']:
                        paste_image = notes_info_list['normal'][id]['image']
                        notes_info_list['long'][id] = {
                            'image': paste_image,
                            'size': ((note_image_width + fix_note_image_width * 2) * long_note_length, note_image_height),
                            'location': note_image_localtion,
                            'location2': note_image_localtion2,
                            'unitid': unitid,
                            'row': row,
                            'row_location': note_in_unit_location,
                        }
                        del notes_info_list['normal'][id]
                    else:
                        notes_info_list['long'][id] = {
                            'image': paste_image,
                            'size': ((note_image_width + fix_note_image_width * 2) * long_note_length, note_image_height),
                            'location': note_image_localtion,
                            'location2': note_image_localtion2,
                            'unitid': unitid,
                            'row': row,
                            'row_location': note_in_unit_location,
                        }

                    # add temp info
                    long_tmp_info[long_id]['image'] = paste_image
                    # add polygon info
                    polygon_list[long_id].append(notes_info_list['long'][id])
                elif long_note_type == 2:
                    if id in notes_info_list['flick']:
                        if long_tmp_info[long_id]['image'] == note_crtcl:
                            paste_image = note_crtcl
                            notes_info_list['flick'][id]['image'] = paste_image

                        notes_info_list['flick'][id]['end'] = True

                        # add polygon info
                        polygon_list['result'][long_id] += 1
                        polygon_list[long_id].append(notes_info_list['flick'][id])
                        continue
                    elif id in notes_info_list['long']:
                        pass
                    else:
                        paste_image = long_tmp_info[long_id]['image']

                        notes_info_list['long'][id] = {
                            'image': paste_image,
                            'size': ((note_image_width + fix_note_image_width * 2) * long_note_length, note_image_height),
                            'location': note_image_localtion,
                            'location2': note_image_localtion2,
                            'unitid': unitid,
                            'row': row,
                            'row_location': note_in_unit_location,
                        }

                    notes_info_list['long'][id]['end'] = True

                    # add polygon info
                    polygon_list['result'][long_id] += 1
                    polygon_list[long_id].append(notes_info_list['long'][id])
                elif long_note_type == 3:
                    if long_tmp_info[long_id]['image'] == note_crtcl:
                        paste_image = note_long_among_crtcl
                    else:
                        paste_image = note_long_among

                    if id in notes_info_list['long']:
                        notes_info_list['long_among'][id] = {
                            'image': paste_image,
                            'size': ((note_image_width + fix_note_image_width * 2) * long_note_length, note_image_height),
                            'length': long_note_length,
                            'location': note_image_localtion,
                            'location2': note_image_localtion2,
                            'unitid': unitid,
                            'row': row,
                            'row_location': note_in_unit_location,
                        }
                        del notes_info_list['long'][id]
                    elif id in notes_info_list['long_among']:
                        if long_tmp_info[long_id]['image'] == note_crtcl:
                            notes_info_list['long_among'][id]['image'] = note_long_among_crtcl
                        else:
                            notes_info_list['long_among'][id]['image'] = note_long_among
                    elif id in notes_info_list['long_among_unvisible']:
                        notes_info_list['long_among'][id] = {
                            'image': paste_image,
                            'size': ((note_image_width + fix_note_image_width * 2) * long_note_length, note_image_height),
                            'length': long_note_length,
                            'location': note_image_localtion,
                            'location2': note_image_localtion2,
                            'unitid': unitid,
                            'row': row,
                            'row_location': note_in_unit_location,
                        }
                        del notes_info_list['long_among_unvisible'][id]
                    else:
                        notes_info_list['long_among'][id] = {
                            'image': paste_image,
                            'size': ((note_image_width + fix_note_image_width * 2) * long_note_length, note_image_height),
                            'length': long_note_length,
                            'location': note_image_localtion,
                            'location2': note_image_localtion2,
                            'unitid': unitid,
                            'row': row,
                            'row_location': note_in_unit_location,
                        }

                    # add polygon info
                    polygon_list[long_id].append(notes_info_list['long_among'][id])
                elif long_note_type == 5:
                    if long_tmp_info[long_id]['image'] == note_crtcl:
                        paste_image = note_long_among_unvisible_crtcl
                    else:
                        paste_image = note_long_among_unvisible

                    if id in notes_info_list['long_among_unvisible']:
                        if long_tmp_info[long_id]['image'] == note_crtcl:
                            notes_info_list['long_among_unvisible'][id]['image'] = note_long_among_unvisible_crtcl
                        else:
                            notes_info_list['long_among_unvisible'][id]['image'] = note_long_among_unvisible
                    elif id in notes_info_list['long']:
                        notes_info_list['long_among_unvisible'][id] = {
                            'image': paste_image,
                            'size': ((note_image_width + fix_note_image_width * 2) * long_note_length, note_image_height),
                            'length': long_note_length,
                            'location': note_image_localtion,
                            'location2': note_image_localtion2,
                            'unitid': unitid,
                            'row': row,
                            'row_location': note_in_unit_location,
                        }
                        del notes_info_list['long'][id]
                    else:
                        x, y, note_in_unit_location = get_location(long_note_length, unit_location, note_in_unit_location_index, row, len(list), type=35)
                        note_image_localtion = (x, y)

                        # check new row
                        note_image_localtion2 = None
                        if unitid % 4 == 0 and note_in_unit_location_index == 0:
                            note_image_localtion2 = (x - unit_width - delta_unit_width, image_height - y - note_image_height)

                        notes_info_list['long_among_unvisible'][id] = {
                            'image': paste_image,
                            'size': ((note_image_width + fix_note_image_width * 2) * long_note_length, note_image_height),
                            'length': long_note_length,
                            'location': note_image_localtion,
                            'location2': note_image_localtion2,
                            'unitid': unitid,
                            'row': row,
                            'row_location': note_in_unit_location,
                        }
                    # add polygon info
                    polygon_list[long_id].append(notes_info_list['long_among_unvisible'][id])
                else:
                    print(str(long_note_type) + 'is not support (score_note_type = 3)')
                    break

        last_unitid = unitid

    # paste note
    for id, note in notes_info_list['normal'].items():
        paste_image = note['image'].resize(note['size'], Image.ANTIALIAS)
        music_score_image.paste(paste_image, note['location'], paste_image)

        if note['location2'] is not None:
            music_score_image.paste(paste_image, note['location2'], paste_image)

    # paste flick
    for id, flick in notes_info_list['flick'].items():
        if flick['image'] == note_crtcl:
            arrow_image = note_flick_arrow_crtcl[flick['arrowtype']][int(flick['length'] / 2) - 1]
        else:
            arrow_image = note_flick_arrow[flick['arrowtype']][int(flick['length'] / 2) - 1]

        paste_image = flick['image'].resize(flick['size'], Image.ANTIALIAS)
        paste_arrow_image = arrow_image.resize((int(arrow_image.size[0] / 4), int(arrow_image.size[1] / 4)), Image.ANTIALIAS)

        music_score_image.paste(paste_image, flick['location'], paste_image)
        music_score_image.paste(paste_arrow_image,
                                (int(flick['location'][0] + (paste_image.size[0] - paste_arrow_image.size[0]) / 2),
                                 int(flick['location'][1] - paste_arrow_image.size[1] * 0.8)),
                                paste_arrow_image)

        if flick['location2'] is not None:
            music_score_image.paste(paste_image, flick['location2'], paste_image)
            music_score_image.paste(paste_arrow_image,
                                    (int(flick['location2'][0] + (paste_image.size[0] - paste_arrow_image.size[0]) / 2),
                                     int(flick['location2'][1] - paste_arrow_image.size[1] * 0.8)),
                                    paste_arrow_image)

    # paste long
    for id, long in notes_info_list['long'].items():
        paste_image = long['image'].resize(long['size'], Image.ANTIALIAS)
        music_score_image.paste(paste_image, long['location'], paste_image)

        if long['location2'] is not None:
            music_score_image.paste(paste_image, long['location2'], paste_image)

    # paste long among
    for id, long_among in notes_info_list['long_among'].items():
        base_image = note_long.resize(long_among['size'], Image.ANTIALIAS)
        paste_image = long_among['image'].resize(
            (int(long_among['image'].size[0] / 10 * long_among['length']),
             int(long_among['image'].size[1] / 10 * long_among['length']))
            , Image.ANTIALIAS)
        music_score_image.paste(paste_image,
                                (long_among['location'][0] + int((base_image.size[0] - paste_image.size[0]) / 2),
                                 long_among['location'][1] + int((base_image.size[1] - paste_image.size[1]) / 2)),
                                paste_image)

        if long_among['location2'] is not None:
            music_score_image.paste(paste_image,
                                    (long_among['location2'][0] + int((base_image.size[0] - paste_image.size[0]) / 2),
                                     long_among['location2'][1] + int((base_image.size[1] - paste_image.size[1]) / 2)),
                                    paste_image)

    # paste long among unvisible
    for id, long_among_unvisible in notes_info_list['long_among_unvisible'].items():
        paste_image = long_among_unvisible['image'].resize(long_among_unvisible['size'], Image.ANTIALIAS)
        music_score_image.paste(paste_image, long_among_unvisible['location'], paste_image)

        if long_among_unvisible['location2'] is not None:
            music_score_image.paste(paste_image, long_among_unvisible['location2'], paste_image)

    return music_score_image


def get_location(note_length, unit_location, note_in_unit_location_index, row, length, type=None):
    note_in_unit_location = int(unit_height / length * note_in_unit_location_index)

    if type == 35:
        x = unit_location[0] + (row - 2) * (note_image_width + fix_note_image_width)
    else:
        if note_length >= 6:
            x = unit_location[0] + (row - 2) * (note_image_width + fix_note_image_width)
        elif note_length % 2 == 0:
            if note_length == 2:
                x = unit_location[0] + (row - note_length) * (note_image_width + fix_note_image_width)
            else:
                x = unit_location[0] + (row - int(note_length / 2)) * (note_image_width + fix_note_image_width) - fix_note_image_width
        else:
            x = unit_location[0] + (int(row - note_length / 2)) * (note_image_width + fix_note_image_width) - fix_note_image_width
    y = unit_location[1] - note_in_unit_location - int(note_image_height / 2)

    return x, y, note_in_unit_location
