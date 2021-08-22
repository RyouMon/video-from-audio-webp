from os.path import join
from unittest import TestCase
from unittest.mock import MagicMock, patch, call
import pipelines


class PipelineManagerTest(TestCase):

    def assert_manager_processes_has_output(self, processes):
        for i, process in enumerate(processes):
            self.assertEqual(process, f'output{i+1}')

    @staticmethod
    def prepare_n_pipeline_mocks(n):
        pipeline_list = [MagicMock() for _ in range(n)]
        for i, pipeline in enumerate(pipeline_list):
            pipeline.process.return_value = f'output{i+1}', f'context{i+1}'
        return pipeline_list

    @staticmethod
    def prepare_output_stream_mocks(n):
        mocks = [MagicMock() for _ in range(n)]
        for mock in mocks:
            mock.run_async.return_value.wait.return_value = 0
            mock.run_async.return_value.returncode = 0
        return mocks

    @staticmethod
    def get_mock_settings(debug=True):
        mock_settings = MagicMock()
        mock_settings.DEBUG = debug
        return mock_settings

    @patch('pipelines.load_object')
    def test_from_settings(self, mock_load_object):
        # prepare mock load_object
        pipeline_classes = [MagicMock(), MagicMock(), MagicMock()]
        parser = MagicMock()
        mock_load_object.side_effect = pipeline_classes

        # prepare settings module
        pipeline_paths = ['a', 'b', 'c']
        settings = MagicMock()
        settings.PIPELINES = pipeline_paths

        manager = pipelines.PipelineManager.from_settings(settings, parser)

        calls = [call('a'), call('b'), call('c')]
        mock_load_object.assert_has_calls(calls)

        for pipeline_cls in pipeline_classes:
            pipeline_cls.assert_called_once_with(settings)
            pipeline_cls.add_arguments.assert_called_once_with(parser)

        for pipeline, pipeline_cls in zip(manager.pipelines, pipeline_classes):
            self.assertEqual(pipeline, pipeline_cls.return_value)

    ############################
    # Test preparing processes #
    ############################

    @patch('pipelines.TemporaryDirectory')
    def test_prepare_processes_when_have_one_pipeline(self, mock_dir):
        pipeline_list = self.prepare_n_pipeline_mocks(1)
        manager = pipelines.PipelineManager(*pipeline_list, settings=self.get_mock_settings())

        processes = manager._prepare_processes('infile', 'outfile', 'context0')

        self.assertEqual(processes[0], 'output1')
        pipeline_list[0].process.assert_called_once_with('infile', 'outfile', 'context0')

    @patch('pipelines.TemporaryDirectory')
    def test_prepare_processes_when_have_two_pipelines(self, mock_dir):
        mock_dir().name = 'temp'
        pipeline_list = self.prepare_n_pipeline_mocks(2)
        manager = pipelines.PipelineManager(*pipeline_list, settings=self.get_mock_settings())

        processes = manager._prepare_processes('infile', 'outfile', 'context0')

        self.assert_manager_processes_has_output(processes)
        pipeline_list[0].process.assert_called_once_with('infile', join('temp', 'step1.mp4'), 'context0')
        pipeline_list[1].process.assert_called_once_with(join('temp', 'step1.mp4'), 'outfile', 'context1')

    @patch('pipelines.TemporaryDirectory')
    def test_prepare_processes_when_have_three_pipelines(self, mock_dir):
        mock_dir().name = 'temp'
        pipeline_list = self.prepare_n_pipeline_mocks(3)
        manager = pipelines.PipelineManager(*pipeline_list, settings=self.get_mock_settings())

        processes = manager._prepare_processes('infile', 'outfile', 'context0')

        self.assert_manager_processes_has_output(processes)
        pipeline_list[0].process.assert_called_once_with('infile', join('temp', 'step1.mp4'), 'context0')
        pipeline_list[1].process.assert_called_once_with(join('temp', 'step1.mp4'), join('temp', 'step2.mp4'), 'context1')
        pipeline_list[2].process.assert_called_once_with(join('temp', 'step2.mp4'), 'outfile', 'context2')

    @patch('pipelines.TemporaryDirectory')
    def test_prepare_processes_when_have_ten_pipelines(self, mock_dir):
        mock_dir().name = 'temp'
        pipeline_list = self.prepare_n_pipeline_mocks(10)
        manager = pipelines.PipelineManager(*pipeline_list, settings=self.get_mock_settings())

        processes = manager._prepare_processes('infile', 'outfile', 'context0')

        self.assert_manager_processes_has_output(processes)
        pipeline_list[0].process.assert_called_once_with('infile', join('temp', 'step1.mp4'), 'context0')
        pipeline_list[-1].process.assert_called_once_with(join('temp', 'step9.mp4'), 'outfile', 'context9')

        for i, pipeline in enumerate(pipeline_list[1:-1]):
            pipeline.process.assert_called_once_with(
                join('temp', f'step{i+1}.mp4'),
                join('temp', f'step{i+2}.mp4'),
                f'context{i+1}'
            )

    ##########################
    # Test running processes #
    ##########################

    def test_run_process_return_0(self):
        output_streams = self.prepare_output_stream_mocks(3)
        manager = pipelines.PipelineManager(*self.prepare_n_pipeline_mocks(3), settings=self.get_mock_settings())

        code = manager._run_processes(*output_streams, quiet=True)

        self.assertEqual(code, 0)
        for process in output_streams:
            process.run_async.assert_called_once_with(quiet=True)
            process.run_async.return_value.wait.assert_called_once()

    def test_run_process_return_1(self):
        output_streams = self.prepare_output_stream_mocks(3)
        output_streams[0].run_async.return_value.wait.return_value = 1
        output_streams[0].run_async.return_value.returncode = 1
        manager = pipelines.PipelineManager(*self.prepare_n_pipeline_mocks(3), settings=self.get_mock_settings())

        code = manager._run_processes(*output_streams, quiet=True)

        self.assertEqual(code, 1)
        output_streams[0].run_async.assert_called_once_with(quiet=True)
        output_streams[0].run_async.return_value.wait.return_value = 1

        for process in output_streams[1:]:
            process.run_async.assert_not_called()
            process.run_async.return_value.wait.assert_not_called()
