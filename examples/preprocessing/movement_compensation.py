"""
.. _ex-movement-comp:

==============================================
Maxwell filter data with movement compensation
==============================================

Demonstrate movement compensation on simulated data. The simulated data
contains bilateral activation of auditory cortices, repeated over 14
different head rotations (head center held fixed). See the following for
details:

    https://github.com/mne-tools/mne-misc-data/blob/master/movement/simulate.py

"""
# Authors: Eric Larson <larson.eric.d@gmail.com>
#
# License: BSD-3-Clause
# Copyright the MNE-Python contributors.

# %%

import mne
from mne.preprocessing import maxwell_filter

print(__doc__)

data_path = mne.datasets.misc.data_path(verbose=True) / "movement"

head_pos = mne.chpi.read_head_pos(data_path / "simulated_quats.pos")
raw = mne.io.read_raw_fif(data_path / "simulated_movement_raw.fif")
raw_stat = mne.io.read_raw_fif(data_path / "simulated_stationary_raw.fif")

# %%
# Visualize the "subject" head movements. By providing the measurement
# information, the distance to the nearest sensor in each direction
# (e.g., left/right for the X direction, forward/backward for Y) can
# be shown in blue, and the destination (if given) shown in red.

mne.viz.plot_head_positions(
    head_pos, mode="traces", destination=raw.info["dev_head_t"], info=raw.info
)

# %%
# This can also be visualized using a quiver.

mne.viz.plot_head_positions(
    head_pos, mode="field", destination=raw.info["dev_head_t"], info=raw.info
)

# %%
# Process our simulated raw data (taking into account head movements).

# extract our resulting events
events = mne.find_events(raw, stim_channel="STI 014")
events[:, 2] = 1
raw.plot(events=events)

topo_kwargs = dict(times=[0, 0.1, 0.2], ch_type="mag", vlim=(-500, 500))

# %%
# First, take the average of stationary data (bilateral auditory patterns).
evoked_stat = mne.Epochs(raw_stat, events, 1, -0.2, 0.8).average()
fig = evoked_stat.plot_topomap(**topo_kwargs)
fig.suptitle("Stationary")

# %%
# Second, take a naive average, which averages across epochs that have been
# simulated to have different head positions and orientations, thereby
# spatially smearing the activity.
epochs = mne.Epochs(raw, events, 1, -0.2, 0.8)
evoked = epochs.average()
fig = evoked.plot_topomap(**topo_kwargs)
fig.suptitle("Moving: naive average")

# %%
# Third, use raw movement compensation (restores pattern).
raw_sss = maxwell_filter(raw, head_pos=head_pos, mc_interp="hann")
evoked_raw_mc = mne.Epochs(raw_sss, events, 1, -0.2, 0.8).average()
fig = evoked_raw_mc.plot_topomap(**topo_kwargs)
fig.suptitle("Moving: movement compensated (raw)")

# %%
# Fourth, use evoked movement compensation. For these data, which contain
# very large rotations, it does not as cleanly restore the pattern.
evoked_evo_mc = mne.epochs.average_movements(epochs, head_pos=head_pos)
fig = evoked_evo_mc.plot_topomap(**topo_kwargs)
fig.suptitle("Moving: movement compensated (evoked)")
