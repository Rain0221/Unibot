import functools
import numpy

import api


class LevelEstimator:

    def __init__(self, points):
        self.points = numpy.array(points)

        for level in range(5, 37):
            try:
                self.print_average(level)
            except:
                pass
        print()

    def estimate(self, adjust, level, music_difficulty):
        level = LevelEstimator.adjust_level_by_music_difficulty(level, music_difficulty)

        min_level, max_level, max_r = 0, 20, 0.5
        r = (level - min_level) / (max_level - min_level) * max_r if min_level < level < max_level else max_r

        adjust = (
            + self.normalizer(adjust, level) * 0.5
            + self.polynomial(adjust, level) * r
        )

        return adjust

    def normalizer(self, adjust, level):
        weights = 4 - abs(self.points[:, 1] - level)
        adjusts, weights = self.points[:, 0][weights > 0], weights[weights > 0]

        mean = numpy.average(adjusts, weights=weights)
        std = numpy.average((adjusts - mean) ** 2, weights=weights) ** 0.5

        return (adjust - mean) / std

    def polynomial(self, adjust, level):
        weights = 5 - abs(self.points[:, 1] - level)
        adjusts, levels, weights = self.points[:, 0][weights > 0], self.points[:, 1][weights > 0], weights[weights > 0]

        f = numpy.polyfit(adjusts, levels, deg=1, w=weights)
        if f[0] < 0:
            print(level, f)
            return 0

        f = numpy.poly1d(f)

        return f(adjust) - level

    def print_average(self, level):
        weights = 4 - abs(self.points[:, 1] - level)
        adjusts, weights = self.points[:, 0][weights > 0], weights[weights > 0]

        mean = numpy.average(adjusts, weights=weights)
        std = numpy.average((adjusts - mean) ** 2, weights=weights) ** 0.5

        print(level, mean, std)

    @staticmethod
    def adjust_level_by_music_difficulty(level, music_difficulty, type='forward'):
        assert type in ('forward', 'backward')

        adjust = {
            'easy': 1.0,
            'normal': 0.5,
            'hard': 0.0,
            'expert': -0.5,
            'master': -1.0,
        }.get(music_difficulty, 0)
        if type == 'backward':
            adjust *= -1

        return level + adjust

    @staticmethod
    def adjust_constant(level, music_difficulty, multi_live_hot=.0, published_time=0):
        level = LevelEstimator.adjust_level_by_music_difficulty(level, music_difficulty)

        min_level, max_level, max_r = 30, 40, 1
        r = (level - min_level) / (max_level - min_level) * max_r if min_level < level < max_level else 0

        return (
            + multi_live_hot / 36
            - 0.5 / (published_time / (1000 * 60 * 60 * 24) + 1)
        ) * (1 - r)

    @staticmethod
    def adjust_count(level, music_difficulty, count, available_count, clear_count):
        level = LevelEstimator.adjust_level_by_music_difficulty(level, music_difficulty)

        min_level, max_level, max_r = 15, 40, 0.5
        r = (level - min_level) / (max_level - min_level) * max_r if min_level < level < max_level else 0

        adjust_count = (
            1
            * count ** r
            * available_count ** r
            * clear_count ** (1 - r * 2)
        )

        return adjust_count


class HotEstimator:

    def __init__(self, points):
        self.points = numpy.array(points)
        self.mean = numpy.mean(self.points)
        self.std = numpy.std(self.points)

    def estimate(self, point):
        return (point - self.mean) / self.std

    @staticmethod
    def published_times(published_at, max_event_end_time):
        if published_at < 1601445600000:
            published_at = 1601445600000

        time = max_event_end_time - published_at
        time_adjust = time

        for event in api.Sekai.get_database('events'):
            if event['eventType'] == 'cheerful_carnival' and event['aggregateAt'] > published_at:
                time_adjust -= event['aggregateAt'] - max(event['startAt'], published_at)

        return time, time_adjust


if __name__ == '__main__':
    level_estimator = LevelEstimator([
        (0.0, 26),
        (0.1, 27),
        (0.2, 28),
        (0.3, 29),
        (0.4, 30),
        (0.5, 31),
        (0.6, 32),
        (0.7, 33),
        (0.8, 34),
        (0.9, 35),
        (1.0, 36),
    ])

    print(level_estimator.polynomial(0.45, 30))
