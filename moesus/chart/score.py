import dataclasses
import functools
import pprint
import re
import typing


@dataclasses.dataclass
class Note:
    bar: float
    lane: int
    width: int
    type: int

    def __hash__(self) -> int:
        return hash(str(self))


@dataclasses.dataclass
class Tap(Note):

    def __hash__(self) -> int:
        return hash(str(self))


@dataclasses.dataclass
class Directional(Note):
    tap: typing.Optional[Note] = dataclasses.field(default=None, repr=False)

    def __hash__(self) -> int:
        return hash(str(self))


@dataclasses.dataclass
class Slide(Note):
    channel: int = 0

    tap: typing.Optional[Note] = dataclasses.field(default=None, repr=False)
    directional: typing.Optional[Note] = dataclasses.field(default=None, repr=False)
    next: typing.Optional['Note'] = dataclasses.field(default=None, repr=False)
    head: typing.Optional[Note] = dataclasses.field(default=None, repr=False)

    def __hash__(self) -> int:
        return hash(str(self))

    def is_path_note(self):
        if self.type != 3:
            return True

        if self.directional:
            return True

        if self.tap is None and self.directional is None:
            return True

        return False


@dataclasses.dataclass
class Event:
    bar: float
    bpm: typing.Optional[float] = None
    bar_length: typing.Optional[int] = None
    sentence_length: int = None
    section: str = None

    def __or__(self, other):
        assert self.bar <= other.bar
        return Event(
            bar=other.bar,
            bpm=other.bpm or self.bpm,
            bar_length=other.bar_length or self.bar_length,
            section=other.section or self.section,
            sentence_length=other.sentence_length or self.sentence_length,
        )


class Line:
    type: str
    header: str
    data: str

    def __init__(self, line: str):
        line = line.strip()

        if match := re.match(r'^#(\w+)\s+(.*)$', line):
            self.type = 'meta'
            self.header, self.data = match.groups()

        elif match := re.match(r'^#(\w+):\s*(.*)$', line):
            self.type = 'score'
            self.header, self.data = match.groups()

        else:
            self.type = 'comment'
            self.header, self.data = 'comment', line


class Score:

    def __init__(self, lines: list[Line] = None, events: list[Event] = None, notes: list[Note] = None) -> None:
        self.bpm_map = {}
        self.events: list[Event] = []
        self.notes: list[Note] = []

        if lines:
            for line in lines:
                for object in self.parse_line(line):
                    if isinstance(object, Event):
                        self.events.append(object)
                    elif isinstance(object, Note):
                        self.notes.append(object)

        if events:
            self.events += events

        if notes:
            self.notes += notes

        self.events.sort(key=lambda event: event.bar)
        self.notes = sorted(set(self.notes), key=lambda note: note.bar)

        self.events = self.parse_events(self.events)
        self.notes = self.parse_notes(self.notes)

    def parse_line(self, line: Line):
        if match := re.match(r'^(\d\d\d)02$', line.header):
            yield Event(bar=int(match.group(1)) + 0.0, bar_length=float(line.data))

        elif match := re.match(r'^BPM(..)$', line.header):
            self.bpm_map[match.group(1)] = float(line.data)

        elif match := re.match(r'^(\d\d\d)08$', line.header):
            for beat, data in self.parse_data(line.data):
                yield Event(bar=int(match.group(1)) + beat, bpm=self.bpm_map[data])

        elif match := re.match(r'^(\d\d\d)1(.)$', line.header):
            for beat, data in self.parse_data(line.data):
                yield Tap(bar=int(match.group(1)) + beat, lane=int(match.group(2), 36), width=int(data[1], 36), type=int(data[0], 36))

        elif match := re.match(r'^(\d\d\d)3(.)(.)$', line.header):
            for beat, data in self.parse_data(line.data):
                yield Slide(bar=int(match.group(1)) + beat, lane=int(match.group(2), 36), width=int(data[1], 36), type=int(data[0], 36), channel=int(match.group(3), 36))

        elif match := re.match(r'^(\d\d\d)5(.)$', line.header):
            for beat, data in self.parse_data(line.data):
                yield Directional(bar=int(match.group(1)) + beat, lane=int(match.group(2), 36), width=int(data[1], 36), type=int(data[0], 36))

    @functools.lru_cache()
    def get_time_event(self, bar):
        t = 0.0
        event = Event(bar=0.0, bpm=120.0, bar_length=4.0, sentence_length=4)

        for i in range(len(self.events)):
            event = event | self.events[i]
            if i+1 == len(self.events) or self.events[i+1].bar > bar:
                t += event.bar_length * 60 / event.bpm * (bar - event.bar)
                break
            else:
                t += event.bar_length * 60 / event.bpm * (self.events[i+1].bar - event.bar)

        return t, event

    def get_time(self, bar):
        return self.get_time_event(bar)[0]

    def get_event(self, bar):
        return self.get_time_event(bar)[1]

    def get_time_delta(self, bar_from, bar_to):
        return self.get_time(bar_to) - self.get_time(bar_from)

    @functools.lru_cache()
    def get_bar_event(self, time):
        t = 0.0
        event = Event(bar=0.0, bpm=120.0, bar_length=4.0, sentence_length=4)

        for i in range(len(self.events)):
            event = event | self.events[i]
            if i+1 == len(self.events) or t + event.bar_length * 60 / event.bpm * (self.events[i+1].bar - event.bar) > time:
                break
            else:
                t += event.bar_length * 60 / event.bpm * (self.events[i+1].bar - event.bar)

        bar = event.bar + (time - t) / (event.bar_length * 60 / event.bpm)

        return bar, event

    def get_bar(self, time):
        return self.get_bar_event(time)[0]

    @staticmethod
    def parse_events(sorted_events: list[Event]):
        events: list[Event] = []

        for event in sorted_events:
            if len(events) and event.bar == events[-1].bar:
                events[-1].bpm = event.bpm or events[-1].bpm
                events[-1].bar_length = event.bar_length or events[-1].bar_length
            else:
                events.append(event)

        return events

    @staticmethod
    def parse_notes(sorted_notes: list[Note]):
        notes: list[Note] = list(sorted_notes)
        note_dict: dict[float, list[Note]] = {}
        for note in sorted_notes:
            if note.bar not in note_dict:
                note_dict[note.bar] = []
            note_dict[note.bar].append(note)

        for i, note in enumerate(sorted_notes):
            if isinstance(note, Directional):
                directional = note

                for note in note_dict[directional.bar]:
                    if isinstance(note, Tap):
                        tap = note
                        if tap.bar == directional.bar and tap.lane == directional.lane and tap.width == directional.width:
                            notes.remove(tap)
                            note_dict[directional.bar].remove(tap)
                            directional.tap = tap
                            break

        for i, note in enumerate(sorted_notes):
            if isinstance(note, Slide):
                slide = note
                if slide.head is None:
                    slide.head = slide

                for note in note_dict[slide.bar]:
                    if isinstance(note, Tap):
                        tap = note
                        if tap.bar == slide.bar and tap.lane == slide.lane and tap.width == slide.width:
                            notes.remove(tap)
                            note_dict[slide.bar].remove(tap)
                            slide.tap = tap
                            break

                for note in note_dict[slide.bar]:
                    if isinstance(note, Directional):
                        directional = note
                        if directional.bar == slide.bar and directional.lane == slide.lane and directional.width == slide.width:
                            notes.remove(directional)
                            note_dict[slide.bar].remove(directional)
                            slide.directional = directional
                            if directional.tap is not None:
                                slide.tap = directional.tap

                            break

                if slide.type != 2:
                    for note in sorted_notes[i+1:]:
                        if isinstance(note, Slide):
                            if note.channel == slide.channel:
                                slide.next = note
                                note.head = slide.head
                                break

        return notes

    @staticmethod
    def parse_data(data: str):
        for i in range(0, len(data), 2):
            if data[i: i+2] != '00':
                yield i / (len(data)), data[i: i+2]

    def rebase(self, events: list[Event], offset=0.0) -> 'Score':
        score = Score(events=events)

        for note_0 in self.notes:
            if isinstance(note_0, Tap):
                score.notes.append(dataclasses.replace(
                    note_0,
                    bar=score.get_bar(self.get_time(note_0.bar) - offset),
                ))
            elif isinstance(note_0, Directional):
                score.notes.append(dataclasses.replace(
                    note_0,
                    bar=score.get_bar(self.get_time(note_0.bar) - offset),
                    tap=None,
                ))
                if note_0.tap:
                    score.notes.append(dataclasses.replace(
                        note_0.tap,
                        bar=score.get_bar(self.get_time(note_0.tap.bar) - offset),
                    ))
            elif isinstance(note_0, Slide):
                score.notes.append(dataclasses.replace(
                    note_0,
                    bar=score.get_bar(self.get_time(note_0.bar) - offset),
                    tap=None,
                    directional=None,
                    next=None,
                    head=None,
                ))
                if note_0.tap:
                    score.notes.append(dataclasses.replace(
                        note_0.tap,
                        bar=score.get_bar(self.get_time(note_0.tap.bar) - offset),
                    ))
                if note_0.directional:
                    score.notes.append(dataclasses.replace(
                        note_0.directional,
                        bar=score.get_bar(self.get_time(note_0.directional.bar) - offset),
                        tap=None,
                    ))
                    if note_0.directional.tap and note_0.directional.tap is not note_0.tap:
                        score.notes.append(dataclasses.replace(
                            note_0.directional.tap,
                            bar=score.get_bar(self.get_time(note_0.directional.tap.bar) - offset),
                        ))

        score.notes.sort(key=lambda note: note.bar)
        score.notes = score.parse_notes(score.notes)

        return score