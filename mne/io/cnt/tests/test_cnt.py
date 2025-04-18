# Authors: The MNE-Python contributors.
# License: BSD-3-Clause
# Copyright the MNE-Python contributors.

import numpy as np
import pytest
from numpy.testing import assert_array_equal

from mne import pick_types
from mne.annotations import read_annotations
from mne.datasets import testing
from mne.io.cnt import read_raw_cnt
from mne.io.tests.test_raw import _test_raw_reader

data_path = testing.data_path(download=False)
fname = data_path / "CNT" / "scan41_short.cnt"
# Contains bad spans and could not be read properly before PR #12393
fname_bad_spans = data_path / "CNT" / "test_CNT_events_mne_JWoess_clipped.cnt"


_no_parse = pytest.warns(RuntimeWarning, match="Could not parse")


@testing.requires_testing_data
def test_old_data():
    """Test reading raw cnt files."""
    with _no_parse, pytest.warns(RuntimeWarning, match="number of bytes"):
        raw = _test_raw_reader(
            read_raw_cnt, input_fname=fname, eog="auto", misc=["NA1", "LEFT_EAR"]
        )

    # make sure we use annotations event if we synthesized stim
    assert len(raw.annotations) == 6

    eog_chs = pick_types(raw.info, eog=True, exclude=[])
    assert len(eog_chs) == 2  # test eog='auto'
    assert raw.info["bads"] == ["LEFT_EAR", "VEOGR"]  # test bads

    # the data has "05/10/200 17:35:31" so it is set to None
    assert raw.info["meas_date"] is None


@testing.requires_testing_data
def test_new_data():
    """Test reading raw cnt files with different header."""
    with pytest.warns(RuntimeWarning):
        raw = read_raw_cnt(input_fname=fname_bad_spans, header="new")

    assert raw.info["bads"] == ["F8"]  # test bads


@testing.requires_testing_data
def test_auto_data():
    """Test reading raw cnt files with automatic header."""
    first = pytest.warns(RuntimeWarning, match="Could not define the number of bytes.*")
    second = pytest.warns(RuntimeWarning, match="Annotations are outside")
    third = pytest.warns(RuntimeWarning, match="Omitted 6 annot")
    with first, second, third:
        raw = read_raw_cnt(input_fname=fname_bad_spans)
    # Test that responses are read properly
    assert "KeyPad Response 1" in raw.annotations.description
    assert raw.info["bads"] == ["F8"]

    with _no_parse, pytest.warns(RuntimeWarning, match="number of bytes"):
        raw = _test_raw_reader(
            read_raw_cnt, input_fname=fname, eog="auto", misc=["NA1", "LEFT_EAR"]
        )

    # make sure we use annotations event if we synthesized stim
    assert len(raw.annotations) == 6

    eog_chs = pick_types(raw.info, eog=True, exclude=[])
    assert len(eog_chs) == 2  # test eog='auto'
    assert raw.info["bads"] == ["LEFT_EAR", "VEOGR"]  # test bads

    # the data has "05/10/200 17:35:31" so it is set to None
    assert raw.info["meas_date"] is None


@testing.requires_testing_data
def test_compare_events_and_annotations():
    """Test comparing annotations and events."""
    with _no_parse, pytest.warns(RuntimeWarning, match="Could not define the num"):
        raw = read_raw_cnt(fname)
    events = np.array(
        [[333, 0, 7], [1010, 0, 7], [1664, 0, 109], [2324, 0, 7], [2984, 0, 109]]
    )

    annot = read_annotations(fname)
    assert len(annot) == 6
    assert_array_equal(annot.onset[:-1], events[:, 0] / raw.info["sfreq"])
    assert "STI 014" not in raw.info["ch_names"]


@testing.requires_testing_data
@pytest.mark.filterwarnings("ignore::RuntimeWarning")
def test_reading_bytes():
    """Test reading raw cnt files with different header."""
    raw_16 = read_raw_cnt(fname, preload=True)
    raw_32 = read_raw_cnt(fname_bad_spans, preload=True)

    # Verify that the number of bytes read is correct
    assert len(raw_16) == 3070
    assert len(raw_32) == 90000


@testing.requires_testing_data
def test_bad_spans():
    """Test reading raw cnt files with bad spans."""
    annot = read_annotations(fname_bad_spans)
    temp = "\t".join(annot.description)
    assert "BAD" in temp
