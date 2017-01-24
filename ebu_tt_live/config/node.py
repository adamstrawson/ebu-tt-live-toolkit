from .common import ConfigurableComponent, Namespace, converters, RequiredConfig
from .clocks import clock_by_type
from .carriage import producer_carriage_by_type, consumer_carriage_by_type
from ebu_tt_live import documents
from ebu_tt_live import bindings
from ebu_tt_live.examples import get_example_data
import ebu_tt_live.node as processing_node
from itertools import cycle
from ebu_tt_live.utils import tokenize_english_document
from ebu_tt_live.errors import ConfigurationError
from ebu_tt_live.strings import ERR_CONF_NO_SUCH_NODE
from .adapters import ProducerNodeCarriageAdapter, ConsumerNodeCarriageAdapter


class NodeBase(ConfigurableComponent):
    required_config = Namespace()
    required_config.add_option('id', default='generic_node')


class ProducerMixin(RequiredConfig):

    required_config = Namespace()
    required_config.output = Namespace()
    required_config.output.carriage = Namespace()
    required_config.output.carriage.add_option(
        'type', default='websocket', from_string_converter=producer_carriage_by_type
    )
    required_config.output.add_option('adapters')

    _output = None

    def _create_output(self, config=None):
        self._output = self.config.output
        self._output.carriage = self.config.output.carriage.type.configure_component(
            config, self.config.output.carriage)

        self._output.adapters = ProducerNodeCarriageAdapter.configure_component(
            config=config,
            local_config=self.config.output.adapters,
            producer=self.component,
            carriage=self._output.carriage.component
        )


class ConsumerMixin(RequiredConfig):

    required_config = Namespace()
    required_config.input = Namespace()
    required_config.input.carriage = Namespace()
    required_config.input.carriage.add_option(
        'type', default='websocket', from_string_converter=consumer_carriage_by_type
    )
    required_config.input.add_option('adapters')

    _input = None

    def _create_input(self, config=None):
        self._input = self.config.input
        self._input.carriage = self.config.input.carriage.type.configure_component(
            config, self.config.input.carriage
        )
        self._input.adapters = ConsumerNodeCarriageAdapter.configure_component(
            config=self.config,
            local_config=self.config.input.adapters,
            consumer=self.component,
            carriage=self._input.carriage.component
        )


class SimpleConsumer(ConsumerMixin, NodeBase):
    required_config = Namespace()
    required_config.add_option('id', default='simple-consumer')
    required_config.add_option('verbose', default=False, doc='Log subtitle content on activation changes')
    required_config.clock = Namespace()
    required_config.clock.add_option('type', default='auto', from_string_converter=clock_by_type)

    _input = None

    def _create_component(self, config=None):
        reference_clock = self.config.clock.type(config, None)
        self.component = processing_node.SimpleConsumer(
            node_id=self.config.id,
            reference_clock=reference_clock.component,
            verbose=self.config.verbose
        )

    def __init__(self, config, local_config):
        super(SimpleConsumer, self).__init__(
            config=config,
            local_config=local_config
        )

        self._create_component(config)
        self._create_input(config)


class ReSequencer(ProducerMixin, ConsumerMixin, NodeBase):

    required_config = Namespace()
    required_config.add_option('id', default='re-sequencer')
    required_config.add_option('sequence_identifier', default='ReSequenced1')
    required_config.add_option('segment_length', default=2.0)
    required_config.clock = Namespace()
    required_config.clock.add_option('type', default='local', from_string_converter=clock_by_type)
    required_config.add_option('discard', default=True)

    _output = None
    _clock = None

    def _create_component(self, config=None):
        self._clock = self.config.clock.type(config, self.config.clock)

        self.component = processing_node.ReSequencer(
            node_id=self.config.id,
            reference_clock=self._clock.component,
            discard=self.config.discard,
            segment_length=self.config.segment_length,
            sequence_identifier=self.config.sequence_identifier
        )

    def __init__(self, config, local_config):
        super(ReSequencer, self).__init__(
            config=config,
            local_config=local_config
        )
        self._create_component(config)
        self._create_input(config)
        self._create_output(config)

        self.backend.register_component_start(self)

    def start(self):
        self.backend.call_periodically(self.component.convert_next_segment, interval=self.config.segment_length)


class BufferDelay(ConsumerMixin, ProducerMixin, NodeBase):
    required_config = Namespace()
    required_config.add_option('id', default='buffer-delay')
    required_config.add_option('delay', default=0.0)

    def _create_component(self, config):
        reference_clock = clock_by_type('auto')(config, None)
        self.component = processing_node.BufferDelayNode(
            node_id=self.config.id,
            document_sequence=None,
            carriage_impl=None,
            fixed_delay=self.config.delay,
            reference_clock=reference_clock.component
        )

    def __init__(self, config, local_config):
        super(BufferDelay, self).__init__(config, local_config)

        self._create_component(config)
        self._create_input(config)
        self._create_output(config)


class RetimingDelay(ConsumerMixin, ProducerMixin, NodeBase):
    required_config = Namespace()
    required_config.add_option('id', default='retiming-delay')
    required_config.add_option('delay', default=0.0)
    required_config.add_option('sequence_identifier', default='RetimedSequence1')

    def _create_component(self, config):
        reference_clock = clock_by_type('auto')(config, None)
        self.component = processing_node.RetimingDelayNode(
            node_id=self.config.id,
            document_sequence=self.config.sequence_identifier,
            fixed_delay=self.config.delay,
            reference_clock=reference_clock.component
        )

    def __init__(self, config, local_config):
        super(RetimingDelay, self).__init__(config, local_config)
        self._create_component(config)
        self._create_input(config)
        self._create_output(config)


class SimpleProducer(ProducerMixin, NodeBase):
    required_config = Namespace()
    required_config.add_option('id', default='simple-producer')
    required_config.add_option('show_time', default=False)
    required_config.add_option('sequence_identifier', default='TestSequence1')
    required_config.add_option('interval', default=2.0)
    required_config.clock = Namespace()
    required_config.clock.add_option('type', default='local', from_string_converter=clock_by_type)

    _clock = None
    _output = None

    def _create_component(self, config=None):
        self._clock = self.config.clock.type(config, self.config.clock)
        sequence = documents.EBUTT3DocumentSequence(
            sequence_identifier=self.config.sequence_identifier,
            lang='en-GB',
            reference_clock=self._clock.component
        )

        if self.config.show_time:
            subtitle_tokens = None  # Instead of text we provide the availability time as content.
        else:
            # Let's read our example conversation
            full_text = get_example_data('simple_producer.txt')
            # if do_export:
            #     subtitle_tokens = iter(tokenize_english_document(full_text))
            # else:
            #     # This makes the source cycle infinitely.
            subtitle_tokens = cycle(tokenize_english_document(full_text))

        self.component = processing_node.SimpleProducer(
            node_id=self.config.id,
            document_sequence=sequence,
            producer_carriage=None,
            input_blocks=subtitle_tokens
        )

    def __init__(self, config, local_config):
        super(SimpleProducer, self). __init__(
            config=config,
            local_config=local_config
        )

        self._create_component(config)
        self._create_output(config)

        self.backend.register_component_start(self)

    def start(self):
        self.backend.call_periodically(self.component.resume_producing, interval=self.config.interval)


class EBUTTDEncoder(ProducerMixin, ConsumerMixin, NodeBase):

    required_config = Namespace()
    required_config.add_option('id', default='ebuttd-encoder')
    required_config.add_option('media_time_zero', default='current')
    required_config.add_option('default_namespace', default=False)
    required_config.clock = Namespace()
    required_config.clock.add_option('type', default='local', from_string_converter=clock_by_type)

    _clock = None

    def _create_component(self, config):
        self._clock = self.config.clock.type(config, self.config.clock)
        if self.config.media_time_zero == 'current':
            mtz = self._clock.component.get_time()
        else:
            mtz = bindings.ebuttdt.LimitedClockTimingType(str(self.config.media_time_zero)).timedelta
        self.component = processing_node.EBUTTDEncoder(
            node_id=self.config.id,
            media_time_zero=mtz,
            default_ns=self.config.default_namespace
        )

    def __init__(self, config, local_config):
        super(EBUTTDEncoder, self).__init__(config, local_config)
        self._create_component(config)
        self._create_input(config)
        self._create_output(config)


def nodes_by_type(node_name):
    if node_name == 'simple-consumer':
        return SimpleConsumer
    elif node_name == 'simple-producer':
        return SimpleProducer
    elif node_name == 'resequencer':
        return ReSequencer
    elif node_name == 'ebuttd-encoder':
        return EBUTTDEncoder
    elif node_name == 'buffer-delay':
        return BufferDelay
    elif node_name == 'retiming-delay':
        return RetimingDelay
    else:
        raise ConfigurationError(ERR_CONF_NO_SUCH_NODE.format(
            node_type=node_name
        ))


class UniversalNode(RequiredConfig):
    required_config = Namespace()
    required_config.add_option('type', default=None, from_string_converter=nodes_by_type)


class UniversalNodeList(ConfigurableComponent):
    required_config = Namespace()
    required_config.node1 = node1 = UniversalNode.get_required_config()
    required_config.node2 = node2 = UniversalNode.get_required_config()
    required_config.node3 = node3 = UniversalNode.get_required_config()
    required_config.node4 = node4 = UniversalNode.get_required_config()
    required_config.node5 = node5 = UniversalNode.get_required_config()
    required_config.node6 = node6 = UniversalNode.get_required_config()
    required_config.node7 = node7 = UniversalNode.get_required_config()

    _nodes = None

    @classmethod
    def configure_component(cls, config, local_config, **kwargs):
        instance = cls(config=config, local_config=local_config)

        instance._nodes = []
        for item in [
            instance.config.node1,
            instance.config.node2,
            instance.config.node3,
            instance.config.node4,
            instance.config.node5,
            instance.config.node6,
            instance.config.node7
        ]:
            if item.type is not None:
                instance._nodes.append(item.type.configure_component(config, item))

        return instance


class UniversalNodes(RequiredConfig):
    required_config = Namespace()
    required_config.nodes = Namespace()
    required_config.nodes.type = UniversalNodeList
