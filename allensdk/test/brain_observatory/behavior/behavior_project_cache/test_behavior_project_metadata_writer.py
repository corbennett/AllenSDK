import tempfile
from pathlib import Path
from unittest.mock import patch

import pandas as pd
import pytest

from allensdk.brain_observatory.behavior.behavior_project_cache import \
    VisualBehaviorOphysProjectCache
from allensdk.brain_observatory.behavior.behavior_project_cache.external\
    .behavior_project_metadata_writer import \
    BehaviorProjectMetadataWriter


class TestVBO:
    """Tests project tables for VBO"""
    @classmethod
    def setup_class(cls):

        test_dir = Path(__file__).parent / 'test_data' / 'vbo'

        # Note: these tables will need to be updated if the expected table
        # changes
        cls.expected_behavior_sessions_table = pd.read_csv(
            test_dir / 'behavior_session_table.csv')
        cls.expected_ophys_sessions_table = pd.read_csv(
            test_dir / 'ophys_session_table.csv')
        cls.expected_ophys_experiments_table = pd.read_csv(
            test_dir / 'ophys_experiment_table.csv')
        cls.expected_ophys_cells_table = pd.read_csv(
            test_dir / 'ophys_cells_table.csv')

        cls.session_type_map = (
            cls.expected_behavior_sessions_table
            .set_index('behavior_session_id')[['session_type']]
            .to_dict()['session_type'])

        cls.test_dir = tempfile.TemporaryDirectory()

        bpc = VisualBehaviorOphysProjectCache.from_lims(
            data_release_date=['2021-03-25', '2021-08-12'])
        cls.project_table_writer = BehaviorProjectMetadataWriter(
            behavior_project_cache=bpc,
            out_dir=cls.test_dir.name,
            project_name='',
            data_release_date=''
        )

    def teardown_class(self):
        self.test_dir.cleanup()

    def _get_session_type(self, behavior_session_id, db_conn):
        """
        Note: mocking this because getting session type from pkl file is
        expensive
        """
        return {
            'behavior_session_id': behavior_session_id,
            'session_type': self.session_type_map[behavior_session_id]}

    @pytest.mark.requires_bamboo
    def test_get_behavior_sessions_table(self):
        with patch('allensdk.brain_observatory.'
                   'behavior.behavior_project_cache.'
                   'project_apis.data_io.behavior_project_lims_api.'
                   '_get_session_type_from_pkl_file',
                   wraps=self._get_session_type):
            self.project_table_writer._write_behavior_sessions()
            obtained = pd.read_csv(Path(self.test_dir.name) /
                                   'behavior_session_table.csv')
            pd.testing.assert_frame_equal(
                obtained, self.expected_behavior_sessions_table)

    @pytest.mark.requires_bamboo
    def test_get_ophys_sessions_table(self):
        with patch('allensdk.brain_observatory.'
                   'behavior.behavior_project_cache.'
                   'project_apis.data_io.behavior_project_lims_api.'
                   '_get_session_type_from_pkl_file',
                   wraps=self._get_session_type):
            self.project_table_writer._write_ophys_sessions()
            obtained = pd.read_csv(Path(self.test_dir.name) /
                                   'ophys_session_table.csv')
            pd.testing.assert_frame_equal(
                obtained, self.expected_ophys_sessions_table)

    @pytest.mark.requires_bamboo
    def test_get_ophys_experiments_table(self):
        with patch('allensdk.brain_observatory.'
                   'behavior.behavior_project_cache.'
                   'project_apis.data_io.behavior_project_lims_api.'
                   '_get_session_type_from_pkl_file',
                   wraps=self._get_session_type):
            self.project_table_writer._write_ophys_experiments()
            obtained = pd.read_csv(Path(self.test_dir.name) /
                                   'ophys_experiment_table.csv')
            pd.testing.assert_frame_equal(
                obtained, self.expected_ophys_experiments_table)

    @pytest.mark.requires_bamboo
    def test_get_ophys_cells_table(self):
        self.project_table_writer._write_ophys_cells()
        obtained = pd.read_csv(Path(self.test_dir.name) /
                               'ophys_cells_table.csv')
        pd.testing.assert_frame_equal(
            obtained, self.expected_ophys_cells_table)