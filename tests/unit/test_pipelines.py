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
    def prepare_n_subprocess_mocks(n):
        subprocesses = [MagicMock() for _ in range(n)]
        for i, subprocess in enumerate(subprocesses):
            subprocess.communicate.return_value = f'out{i}', f'err{i}'
        return subprocesses

    @staticmethod
    def prepare_n_mocks(n):
        return [MagicMock() for _ in range(n)]

    @staticmethod
    def get_mock_settings(debug=True):
        mock_settings = MagicMock()
        mock_settings.DEBUG = debug
        return mock_settings

    @patch('pipelines.load_object')
    def test_from_settings(self, mock_load_object):
        # prepare mock load_object
        pipeline_classes = [MagicMock(), MagicMock(), MagicMock()]
        mock_load_object.side_effect = pipeline_classes

        # prepare settings module
        pipeline_paths = ['a', 'b', 'c']
        settings = MagicMock()
        settings.PIPELINES = pipeline_paths

        manager = pipelines.PipelineManager.from_settings(settings)

        calls = [call('a'), call('b'), call('c')]
        mock_load_object.assert_has_calls(calls)

        for pipeline_cls in pipeline_classes:
            pipeline_cls.assert_called_once_with(settings)

        for pipeline, pipeline_cls in zip(manager.pipelines, pipeline_classes):
            self.assertEqual(pipeline, pipeline_cls.return_value)

    def test_process(self):
        pass

    ############################
    # Test preparing processes #
    ############################

    def test_prepare_processes_when_have_one_pipeline(self):
        pipeline_list = self.prepare_n_pipeline_mocks(1)
        manager = pipelines.PipelineManager(*pipeline_list, settings=self.get_mock_settings())

        processes = manager._prepare_processes('infile', 'outfile', 'context0')

        self.assertEqual(processes[0], 'output1')
        pipeline_list[0].process.assert_called_once_with('infile', 'outfile', 'context0')

    def test_prepare_processes_when_have_two_pipelines(self):
        pipeline_list = self.prepare_n_pipeline_mocks(2)
        manager = pipelines.PipelineManager(*pipeline_list, settings=self.get_mock_settings())

        processes = manager._prepare_processes('infile', 'outfile', 'context0')

        self.assert_manager_processes_has_output(processes)
        pipeline_list[0].process.assert_called_once_with('infile', 'pipe:', 'context0')
        pipeline_list[1].process.assert_called_once_with('pipe:', 'outfile', 'context1')

    def test_prepare_processes_when_have_three_pipelines(self):
        pipeline_list = self.prepare_n_pipeline_mocks(3)
        manager = pipelines.PipelineManager(*pipeline_list, settings=self.get_mock_settings())

        processes = manager._prepare_processes('infile', 'outfile', 'context0')

        self.assert_manager_processes_has_output(processes)
        pipeline_list[0].process.assert_called_once_with('infile', 'pipe:', 'context0')
        pipeline_list[1].process.assert_called_once_with('pipe:', 'pipe:', 'context1')
        pipeline_list[2].process.assert_called_once_with('pipe:', 'outfile', 'context2')

    def test_prepare_processes_when_have_ten_pipelines(self):
        pipeline_list = self.prepare_n_pipeline_mocks(10)
        manager = pipelines.PipelineManager(*pipeline_list, settings=self.get_mock_settings())

        processes = manager._prepare_processes('infile', 'outfile', 'context0')

        self.assert_manager_processes_has_output(processes)
        pipeline_list[0].process.assert_called_once_with('infile', 'pipe:', 'context0')
        pipeline_list[-1].process.assert_called_once_with('pipe:', 'outfile', 'context9')

        for i, pipeline in enumerate(pipeline_list[1:-1]):
            pipeline.process.assert_called_once_with('pipe:', 'pipe:', f'context{i+1}')

    ##########################
    # Test running processes #
    ##########################

    def test_run_one_process(self):
        processes = self.prepare_n_mocks(1)
        manager = pipelines.PipelineManager(*self.prepare_n_pipeline_mocks(1), settings=self.get_mock_settings())

        subprocesses = manager._run_processes(*processes, quiet=True)

        self.assertEqual(subprocesses, [process.run_async.return_value for process in processes])
        processes[0].run_async.assert_called_once_with(quiet=True)

    def test_run_two_processes(self):
        processes = self.prepare_n_mocks(2)
        manager = pipelines.PipelineManager(*self.prepare_n_pipeline_mocks(2), settings=self.get_mock_settings())

        subprocesses = manager._run_processes(*processes, quiet=True)

        self.assertEqual(subprocesses, [process.run_async.return_value for process in processes])
        processes[0].run_async.assert_called_once_with(pipe_stdout=True, quiet=True)
        processes[1].run_async.assert_called_once_with(pipe_stdin=True, quiet=True)

    def test_run_three_processes(self):
        processes = self.prepare_n_mocks(3)
        manager = pipelines.PipelineManager(*self.prepare_n_pipeline_mocks(3), settings=self.get_mock_settings())

        subprocesses = manager._run_processes(*processes, quiet=True)

        self.assertEqual(subprocesses, [process.run_async.return_value for process in processes])
        processes[0].run_async.assert_called_once_with(pipe_stdout=True, quiet=True)
        processes[1].run_async.assert_called_once_with(pipe_stdin=True, pipe_stdout=True, quiet=True)
        processes[2].run_async.assert_called_once_with(pipe_stdin=True, quiet=True)

    def test_run_ten_processes(self):
        processes = self.prepare_n_mocks(10)
        manager = pipelines.PipelineManager(*self.prepare_n_pipeline_mocks(10), settings=self.get_mock_settings())

        subprocesses = manager._run_processes(*processes, quiet=True)

        self.assertEqual(subprocesses, [process.run_async.return_value for process in processes])
        processes[0].run_async.assert_called_once_with(pipe_stdout=True, quiet=True)
        processes[-1].run_async.assert_called_once_with(pipe_stdin=True, quiet=True)

        for process in processes[1:-1]:
            process.run_async.assert_called_once_with(pipe_stdin=True, pipe_stdout=True, quiet=True)

    ################################
    # Test processes communication #
    ################################

    def test_connect_one_process(self):
        processes = self.prepare_n_subprocess_mocks(1)
        manager = pipelines.PipelineManager(*self.prepare_n_pipeline_mocks(1), settings=self.get_mock_settings())

        out, err = manager._connect_processes(*processes)

        self.assertEqual(out, 'out0')
        self.assertEqual(err, 'err0')
        processes[0].communicate.assert_called_once_with()

    def test_connect_two_processes(self):
        processes = self.prepare_n_subprocess_mocks(2)
        manager = pipelines.PipelineManager(*self.prepare_n_pipeline_mocks(2), settings=self.get_mock_settings())

        out, err = manager._connect_processes(*processes)

        self.assertEqual(out, 'out1')
        self.assertEqual(err, 'err1')
        processes[0].communicate.assert_called_once_with()
        processes[1].communicate.assert_called_once_with(input='out0')

    def test_connect_three_processes(self):
        processes = self.prepare_n_subprocess_mocks(3)
        manager = pipelines.PipelineManager(*self.prepare_n_pipeline_mocks(3), settings=self.get_mock_settings())

        out, err = manager._connect_processes(*processes)

        self.assertEqual(out, 'out2')
        self.assertEqual(err, 'err2')
        processes[0].communicate.assert_called_once_with()
        processes[1].communicate.assert_called_once_with(input='out0')
        processes[2].communicate.assert_called_once_with(input='out1')

    def test_connect_ten_processes(self):
        processes = self.prepare_n_subprocess_mocks(10)
        manager = pipelines.PipelineManager(*self.prepare_n_pipeline_mocks(10), settings=self.get_mock_settings())

        out, err = manager._connect_processes(*processes)

        self.assertEqual(out, 'out9')
        self.assertEqual(err, 'err9')
        processes[0].communicate.assert_called_once_with()

        for i, process in enumerate(processes[1:]):
            process.communicate.assert_called_once_with(input=f'out{i}')

    ##########################
    # Test waiting processes #
    ##########################

    def test_wait_one_process(self):
        processes = self.prepare_n_subprocess_mocks(1)
        manager = pipelines.PipelineManager(*self.prepare_n_pipeline_mocks(1), settings=self.get_mock_settings())

        code = manager._wait_processes(*processes)

        self.assertEqual(code, processes[0].wait.return_value)
        processes[0].wait.assert_called_once_with()

    def test_wait_two_processes(self):
        processes = self.prepare_n_subprocess_mocks(2)
        manager = pipelines.PipelineManager(*self.prepare_n_pipeline_mocks(2), settings=self.get_mock_settings())

        code = manager._wait_processes(*processes)

        processes[0].wait.assert_called_once_with()
        processes[1].wait.assert_called_once_with()
        processes[1].stdin.close.assert_called_once_with()

    def test_wait_ten_processes(self):
        processes = self.prepare_n_subprocess_mocks(10)
        manager = pipelines.PipelineManager(*self.prepare_n_pipeline_mocks(10), settings=self.get_mock_settings())

        code = manager._wait_processes(*processes)

        processes[0].wait.assert_called_once_with()
        for process in processes[1:]:
            process.wait.assert_called_once_with()
            process.stdin.close.assert_called_once_with()
