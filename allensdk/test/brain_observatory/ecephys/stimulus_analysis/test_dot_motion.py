import os
import pytest
import numpy as np
import pandas as pd

from allensdk.brain_observatory.ecephys.stimulus_analysis import dot_motion as dm


data_dir = '/allen/aibs/informatics/module_test_data/ecephys/stimulus_analysis_fh'


@pytest.mark.skip(reason='Missing implementation prevents us from gathering any metrics.')
@pytest.mark.parametrize('spikes_nwb,expected_csv,analysis_params,units_filter',
                         [
                             #(os.path.join(data_dir, 'data', 'mouse406807_integration_test.spikes.nwb2'),
                             # os.path.join(data_dir, 'expected', 'mouse406807_integration_test.dot_motion.csv'),
                             # {})
                             (os.path.join(data_dir, 'data', 'ecephys_session_773418906.nwb'),
                              os.path.join(data_dir, 'expected', 'ecephys_session_773418906.dot_motion.csv'),
                              {},
                              [914580630, 914580280, 914580278, 914580634, 914580610, 914580290, 914580288, 914580286,
                               914580284, 914580282, 914580294, 914580330, 914580304, 914580292, 914580300, 914580298,
                               914580308, 914580306, 914580302, 914580316, 914580314, 914580312, 914580310, 914580318,
                               914580324, 914580322, 914580320, 914580328, 914580326, 914580334])
                         ])
def test_metrics(spikes_nwb, expected_csv, analysis_params, units_filter, skip_cols=[]):
    """Full intergration tests of metrics table"""
    if not os.path.exists(spikes_nwb):
        pytest.skip('No input spikes file {}.'.format(spikes_nwb))

    analysis_params = analysis_params or {}
    analysis = dm.DotMotion(spikes_nwb, filter=units_filter, **analysis_params)
    # Make sure some of the non-metrics structures are returning valid(ish) tables
    assert(len(analysis.stim_table) > 1)
    assert(set(analysis.unit_ids) == set(units_filter))
    assert(len(analysis.running_speed) == len(analysis.stim_table))
    assert(analysis.stim_table_spontaneous.shape == (3, 5))
    assert(set(analysis.spikes.keys()) == set(units_filter))
    assert(len(analysis.conditionwise_psth) > 1)

    actual_data = analysis.metrics.sort_index()

    expected_data = pd.read_csv(expected_csv)
    expected_data = expected_data.set_index('unit_id')
    expected_data = expected_data.sort_index()  # in theory this should be sorted in the csv, no point in risking it.

    assert(np.all(actual_data.index.values == expected_data.index.values))
    assert(set(actual_data.columns) == (set(expected_data.columns) - set(skip_cols)))

    assert(np.allclose(actual_data['pref_speed_dm'].astype(np.float), expected_data['pref_speed_dm'], equal_nan=True))
    assert(np.allclose(actual_data['pref_dir_dm'].astype(np.float), expected_data['pref_dir_dm'], equal_nan=True))
    assert(np.allclose(actual_data['firing_rate_dm'].astype(np.float), expected_data['firing_rate_dm'], equal_nan=True))
    assert(np.allclose(actual_data['fano_dm'].astype(np.float), expected_data['fano_dm'], equal_nan=True))
    assert(np.allclose(actual_data['speed_tuning_idx_dm'].astype(np.float), expected_data['speed_tuning_idx_dm'],
                       equal_nan=True))
    assert(np.allclose(actual_data['time_to_peak_dm'].astype(np.float), expected_data['time_to_peak_dm'],
                       equal_nan=True))
    assert (np.allclose(actual_data['reliability_dm'].astype(np.float), expected_data['reliability_dm'],
                        equal_nan=True))
    assert (np.allclose(actual_data['lifetime_sparseness_dm'].astype(np.float), expected_data['lifetime_sparseness_dm'],
                        equal_nan=True))
    assert (np.allclose(actual_data['run_mod_dm'].astype(np.float), expected_data['run_mod_dm'], equal_nan=True))
    assert (np.allclose(actual_data['run_pval_dm'].astype(np.float), expected_data['run_pval_dm'], equal_nan=True))
