"""Opening sequence: timing logic and the content/intro.json data."""

import pytest

from game import config
from game.scenes.intro import MAX_CHARS
from game.systems.intro_timeline import (Beat, IntroTimeline, load_intro,
                                         parse_intro, scroll_offset)
from game.ui.text import wrap

BEATS = [Beat("train", 10, "abcd"), Beat("train", 10, "efgh"), Beat("street", 20, "ijkl")]


def test_timeline_plays_through_and_finishes():
    tl = IntroTimeline(BEATS)
    for _ in range(40):
        tl.tick()
    assert tl.done


def test_scene_progress_spans_consecutive_beats():
    tl = IntroTimeline(BEATS)
    for _ in range(15):
        tl.tick()
    assert tl.beat.caption == "efgh"
    assert tl.scene_progress == pytest.approx(15 / 20)
    assert tl.scene_length == 20


def test_confirm_reveals_then_advances():
    tl = IntroTimeline(BEATS)
    tl.confirm()
    assert tl.caption_complete and tl.index == 0
    tl.confirm()
    assert tl.index == 1 and not tl.caption_complete


def test_skip_ends_immediately():
    tl = IntroTimeline(BEATS)
    tl.skip()
    assert tl.done


def test_scroll_brakes_to_a_stop():
    end = scroll_offset(1.0, 100, 5.0)
    near_end = scroll_offset(0.99, 100, 5.0)
    early = scroll_offset(0.10, 100, 5.0) - scroll_offset(0.09, 100, 5.0)
    assert end - near_end < early  # slower at the end than at the start
    assert scroll_offset(0.5, 100, 5.0) == pytest.approx(250.0)


def test_bad_scene_rejected():
    with pytest.raises(ValueError, match="unknown scene"):
        parse_intro({"beats": [{"scene": "boat", "frames": 10, "caption": "x"}]})


def test_intro_content_loads_and_captions_fit():
    data = load_intro(config.INTRO_FILE)
    assert data.beats[0].scene == "train" and data.beats[-1].scene == "street"
    for beat in data.beats:
        assert len(wrap(beat.caption, MAX_CHARS)) <= 3, beat.caption
        assert beat.frames >= len(beat.caption) // 2 + 30, "caption leaves too little time to read"
    assert data.controls_rows


def test_controls_card_text_fits():
    from game.ui.text import BIG_CHAR_W
    data = load_intro(config.INTRO_FILE)
    for keys, action in data.controls_rows:
        assert len(keys) * BIG_CHAR_W <= 88, keys
        assert 100 + len(action) * BIG_CHAR_W <= 244, action
    assert len(data.prompt) * BIG_CHAR_W <= 244
