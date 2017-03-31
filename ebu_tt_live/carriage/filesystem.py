from .base import AbstractProducerCarriage, AbstractConsumerCarriage
from ebu_tt_live.documents import EBUTT3Document
from ebu_tt_live.errors import EndOfData
from ebu_tt_live.utils import RotatingFileBuffer
from datetime import timedelta
import logging
import six
import os
import time


log = logging.getLogger(__name__)


def timedelta_to_str_manifest(timed, time_base):
    if time_base == 'clock' or time_base == 'media':
        hours, seconds = divmod(timed.seconds, 3600)
        hours += timed.days * 24
        minutes, seconds = divmod(seconds, 60)
        milliseconds, _ = divmod(timed.microseconds, 1000)
        return '{:02d}:{:02d}:{:02d}.{:03d}'.format(hours, minutes, seconds, milliseconds)
    elif time_base == 'smpte':
        raise NotImplementedError()
    else:
        raise ValueError()


def timestr_manifest_to_timedelta(timestr, time_base):
    if time_base == 'clock' or time_base == 'media':
        hours, minutes, rest = timestr.split(":")
        seconds, milliseconds = rest.split(".")
        return timedelta(hours=int(hours), minutes=int(minutes), seconds=int(seconds), milliseconds=int(milliseconds))
    elif time_base == 'smpte':
        raise NotImplementedError()
    else:
        raise ValueError()


class FilesystemProducerImpl(AbstractProducerCarriage):
    """
    This class implements a carriage mechanism to output produced documents
    to the file system. Its constructor takes a mandatory argument : the path to
    the desired output folder. If the folder does not exist it will be created.
    Each document handled by this carriage implementation is written in an xml file
    in the output folder.
    Along with the xml files, a manifest_sequenceIdentifier.txt file is also written in the output folder.
    Each time an xml file is written, a line using the following format is added to the manifest :

    `availability_time,path_to_xml_file`

    The manifest file gives the availability time for each document along with the path to the
    corresponding document.
    The timeline used for the availability times is the same as the one used in the documents,
    indeed the carriage implementation uses the same clock (or time reference) as the node that
    produces the documents.
    The writing order and thus the reading order is from top to bottom. Please note that depending on the
    timebase used by the producer node time may loop (going to the next day). It can loop with
    `ttp:timeBase="clock"` or `ttp:timeBase="smpte"`, but not with `ttp:timeBase="media"`.
    If the output folder already exists and it contains a manifest_sequenceIdentifier.txt file for the same
    document sequence, the last line of the existing manifest file is parsed to get the last used sequence number
    and the current sequence is set to start from the next sequence number.
    """

    _manifest_path = None
    _dirpath = None
    _manifest_content = None
    _manifest_time_format = None
    _expects = six.text_type

    def __init__(self, dirpath):
        self._dirpath = dirpath
        if not os.path.exists(self._dirpath):
            os.makedirs(self._dirpath)
        self._manifest_content = ''

    def resume_producing(self):
        while True:
            try:
                self.producer_node.resume_producing()
            except EndOfData:
                break

    def emit_data(self, data, sequence_identifier=None, sequence_number=None,
                  time_base=None, availability_time=None, delay=None, **kwargs):
        if self._manifest_path is None:
            manifest_filename = "manifest_" + sequence_identifier + ".txt"
            self._manifest_path = os.path.join(self._dirpath, manifest_filename)
        # Handle there the switch and checks to handle the string format to use
        # for times in the manifest file depending on your time base.
        filename = '{}_{}.xml'.format(sequence_identifier, sequence_number)
        filepath = os.path.join(self._dirpath, filename)
        with open(filepath, 'w') as f:
            f.write(data)
        # To be able to format the output we need a datetime.time object and
        # not a datetime.timedelta. The next line serves as a converter (adding
        # a time with a timedelta gives a time)
        time_base = time_base
        availability_time = availability_time
        if delay is not None:
            availability_time += timedelta(seconds=delay)
        new_manifest_line = '{},{}\n'.format(timedelta_to_str_manifest(availability_time, time_base), filename)
        self._manifest_content += new_manifest_line
        with open(self._manifest_path, 'a') as f:
            f.write(new_manifest_line)


class FilesystemConsumerImpl(AbstractConsumerCarriage):
    """
    This class is responsible for setting the document object from the xml and set its availability time.
    The document is then sent to the node.
    """

    _provides = six.text_type

    def on_new_data(self, data, **kwargs):
        availability_time_str, xml_content = data

        if xml_content:
            # TODO: Defaulting to media time parsing because that is the broadest. Figure out a nicer solution!
            availability_time = timestr_manifest_to_timedelta(availability_time_str, 'media')
            self.consumer_node.process_document(xml_content, availability_time=availability_time)


class FilesystemReader(object):
    """
    This class is responsible for reading the manifest file and sending the corresponding
    availability times and xml file's content to its _custom_consumer. Important note : the
    manifest file and the xml documents have to be in the same folder (it is the default behavior
    of the producer).
    """
    _dirpath = None
    _manifest_path = None
    _custom_consumer = None
    _manifest_time_format = None
    _do_tail = None

    def __init__(self, manifest_path, custom_consumer, do_tail):
        self._dirpath = os.path.dirname(manifest_path)
        self._manifest_path = manifest_path
        self._custom_consumer = custom_consumer
        self._do_tail = do_tail
        with open(manifest_path, 'r') as manifest:
            self._manifest_lines_iter = iter(manifest.readlines())

    def resume_reading(self):
        with open(self._manifest_path, 'r') as manifest_file:
            while True:
                manifest_line = manifest_file.readline()
                if not manifest_line:
                    if self._do_tail:
                        try:
                            time.sleep(0.5)
                        except KeyboardInterrupt:
                            break
                    else:
                        break
                else:
                    availability_time_str, xml_file_name = manifest_line.rstrip().split(',')
                    xml_file_path = os.path.join(self._dirpath, xml_file_name)
                    xml_content = None
                    with open(xml_file_path, 'r') as xml_file:
                        xml_content = xml_file.read()
                    data = [availability_time_str, xml_content]
                    self._custom_consumer.on_new_data(data)


class SimpleFolderExport(AbstractProducerCarriage):

    _dir_path = None
    _file_name_pattern = None
    _counter = None

    def __init__(self, dir_path, file_name_pattern):
        self._dir_path = dir_path
        if not os.path.exists(dir_path):
            os.makedirs(self._dir_path)
        self._file_name_pattern = file_name_pattern
        self._counter = 0

    def _do_write_document(self, document, **kwargs):
        self._counter += 1
        filename = self._file_name_pattern.format(counter=self._counter)
        filepath = os.path.join(self._dir_path, filename)
        with open(filepath, 'w') as destfile:
            destfile.write(document.get_xml())
            destfile.flush()
        return filepath

    def emit_data(self, data, **kwargs):
        self._do_write_document(data, **kwargs)


class RotatingFolderExport(SimpleFolderExport):
    """
    This carriage mechanism only keeps the last files that fit in its circular buffer. If a new file is written the
    oldest one is discarded. The size of the buffer can be specified. This is useful for use-cases when the entire
    sequence of files is not meant to be kept, only just the right amount to cover the needs of broadcast requirement
    such as timeshift, which allows the viewer to rewind the TV show within a specific limited time range.
    """

    _circular_buf = None

    def __init__(self, dir_path, file_name_pattern, circular_buf_size):
        super(RotatingFolderExport, self).__init__(dir_path, file_name_pattern)
        self._circular_buf = RotatingFileBuffer(maxlen=circular_buf_size)

    def emit_data(self, data, **kwargs):
        file_name = self._do_write_document(data)
        self._circular_buf.append(file_name)
