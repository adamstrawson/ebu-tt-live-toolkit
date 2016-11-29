from abc import ABCMeta, abstractmethod, abstractproperty
import six

# Interfaces
# ==========


class INode(six.with_metaclass(ABCMeta)):
    """
    This is the foundation of all nodes that take part in the processing of subtitle documents.
    The Node should deal with subtitles in a high level interface,
    which is an instance of :class:`<ebu_tt_live.documents.SubtitleDocument>`. That is the interface which should
    be used to communicate with the carriage machanism. See :class:`<ebu_tt_live.carriage.ICarriage>`
    """

    @abstractmethod
    def process_document(self, document, **kwargs):
        """
        The central hook that is meant to implement the main functionality of the node.
        A node must implement this method.
        :param **kwargs: Extra parameters
        :param document: Can be XML, Document object...etc. depending on the carriage implementation
        :return:
        """
        raise NotImplementedError()


class Node(six.with_metaclass(ABCMeta)):


    _node_id = None
    _carriage_impl = None

    def __init__(self, node_id, carriage_impl):
        self._node_id = node_id
        self._carriage_impl = carriage_impl
        self._carriage_impl.register(node=self)

    def __repr__(self):
        return '<{name}, ID:{id} at {address} >'.format(
            name=self.__class__,
            id=self._node_id,
            address=hex(id(self))
        )

    @property
    def node_id(self):
        return self._node_id

    @node_id.setter
    def node_id(self, value):
        self._node_id = value

    def process_document(self, document, **kwargs):
        """
        The central hook that is meant to implement the main functionality of the node.
        A node must implement this method.
        :param **kwargs: Extra parameters
        :param document: Can be XML, Document object...etc. depending on the carriage implementation
        :return:
        """
        raise NotImplementedError()
