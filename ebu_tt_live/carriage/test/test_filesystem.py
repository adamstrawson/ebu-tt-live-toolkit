from unittest import TestCase, skip
from mock import patch, MagicMock
from ebu_tt_live.carriage.filesystem import FilesystemProducerImpl, FilesystemConsumerImpl, FilesystemReader, timestr_manifest_to_timedelta, timedelta_to_str_manifest
from ebu_tt_live.errors import EndOfData, XMLParsingFailed
from ebu_tt_live.documents import EBUTT3Document
from ebu_tt_live.node.interface import IProducerNode, IConsumerNode
from datetime import timedelta
import os
import tempfile
import shutil
import six


class TestFilesystemProducerImpl(TestCase):

    def setUp(self):
        self.test_dir = tempfile.mkdtemp()
        self.test_dir_path = os.path.abspath(self.test_dir)

    def tearDown(self):
        shutil.rmtree(self.test_dir)

    def test_instantiation(self):
        fs_carriage = FilesystemProducerImpl(self.test_dir_path)
        self.assertIsInstance(fs_carriage, FilesystemProducerImpl)

    def test_resume_producing_no_existing_manifest(self):
        node = MagicMock(spec=IProducerNode)
        node.provides.return_value = six.text_type

        def side_effect():
            raise EndOfData()

        node.resume_producing.side_effect = side_effect

        fs_carriage = FilesystemProducerImpl(self.test_dir_path)
        fs_carriage.register_producer_node(node)
        fs_carriage.resume_producing()
        node.resume_producing.assert_called_once()

    def test_emit_document(self):
        data = 'test'
        node = MagicMock(spec=IProducerNode)
        node.provides.return_value = six.text_type
        test_time = timedelta(hours=42, minutes=42, seconds=42, milliseconds=67)
        node.resume_producing.side_effect = EndOfData()
        fs_carriage = FilesystemProducerImpl(self.test_dir_path)
        fs_carriage.register_producer_node(node)
        fs_carriage.resume_producing()
        fs_carriage.emit_data(data, availability_time=test_time, sequence_identifier='testSeq',
                              sequence_number=1, time_base='clock')
        exported_document_path = os.path.join(self.test_dir_path, 'testSeq_1.xml')
        assert os.path.exists(exported_document_path)
        manifest_path = os.path.join(self.test_dir_path, 'manifest_testSeq.txt')
        assert os.path.exists(manifest_path)


class TestFilesystemConsumerImpl(TestCase):

    def setUp(self):
        self.test_data_dir_path = os.path.join(os.path.dirname(__file__), 'test_data')

    def test_on_new_data(self):
        node = MagicMock(spec=IConsumerNode)
        node.expects.return_value = six.text_type
        test_xml_file_path = os.path.join(self.test_data_dir_path, 'testSeq_1.xml')
        with open(test_xml_file_path, 'r') as test_xml_file:
            test_xml = test_xml_file.read()
        data = ["18:42:42.42", test_xml]
        fs_consumer_impl = FilesystemConsumerImpl()
        fs_consumer_impl.register_consumer_node(node)
        fs_consumer_impl.on_new_data(data)
        node.process_document.assert_called_once()


class TestFilesystemReader(TestCase):

    def setUp(self):
        self.test_data_dir_path = os.path.join(os.path.dirname(__file__), 'test_data')

    @patch('ebu_tt_live.carriage.filesystem.FilesystemConsumerImpl')
    def test_resume_reading(self, fs_carriage_impl):
        fs_carriage_impl.on_new_data = MagicMock(return_value=None)
        test_manifest_path = os.path.join(self.test_data_dir_path, 'manifest_testSeq.txt')
        fs_reader = FilesystemReader(test_manifest_path, fs_carriage_impl, False)
        test_xml = None
        with open(test_manifest_path, 'r') as test_manifest:
            manifest_line = test_manifest.readline()
            availability_time_str, test_xml_file_name = manifest_line.rstrip().split(',')
            test_xml_file_path = os.path.join(self.test_data_dir_path, test_xml_file_name)
            with open(test_xml_file_path, 'r') as test_xml_file:
                test_xml = test_xml_file.read()
        fs_reader.resume_reading()
        data = [availability_time_str, test_xml]
        fs_carriage_impl.on_new_data.assert_called_once_with(data)


class TestManifestTimedeltaConversion(TestCase):

    def test_timedelta_to_str_manifest(self):
        test_time = timedelta(hours=42, minutes=42, seconds=42, milliseconds=0)
        expected_time_str = "42:42:42.000"
        test_time_str = timedelta_to_str_manifest(test_time, 'clock')
        self.assertEqual(test_time_str, expected_time_str)
        test_time_str = timedelta_to_str_manifest(test_time, 'media')
        self.assertEqual(test_time_str, expected_time_str)
        self.assertRaises(ValueError, lambda: timedelta_to_str_manifest(test_time, 'test'))

    def test_timestr_manifest_to_timedelta(self):
        test_time_str = "199:12:24.059"
        expected_timedelta = timedelta(hours=199, minutes=12, seconds=24, milliseconds=59)
        test_timedelta = timestr_manifest_to_timedelta(test_time_str, 'media')
        self.assertEqual(test_timedelta, expected_timedelta)
        self.assertRaises(ValueError, lambda: timestr_manifest_to_timedelta(test_time_str, 'test'))
