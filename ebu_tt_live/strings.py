
from gettext import gettext

# ERRORS
ERR_NO_SUCH_COMPONENT = gettext('No such component: {type_name}')
ERR_INCOMPATIBLE_COMPONENT = gettext('Incompatible component: {component} Expected interface: {expected_interface}')
ERR_INCOMPATIBLE_DATA_PROVIDED = gettext('{component} provides incompatible data type: {provides} Expected type: {expects}')
ERR_INCOMPATIBLE_DATA_EXPECTED = gettext('{component} expects incompatible data type: {expects} Provided type: {provides}')
ERR_INCOMPATIBLE_DATA_CONVERSION = gettext('{provides} -> {expects} conversion not possible with converters: {data_adapters}')
ERR_CONV_NO_INPUT = gettext('The converter has no input set')
ERR_TIME_WRONG_FORMAT = gettext('Wrong time format. datetime.timedelta is expected')
ERR_TIME_FORMAT_OVERFLOW = gettext('Time value is out of format range')
ERR_DOCUMENT_SEQUENCE_MISMATCH = gettext('sequenceIdentifier mismatch')
ERR_DOCUMENT_SEQUENCENUMBER_COLLISION = gettext('Sequence number: [{sequence_number}] already present in sequence: [{sequence_identifier}]')
ERR_DECODING_XML_FAILED = gettext('XML document parsing failed')
ERR_SEMANTIC_VALIDATION_TIMING_TYPE = gettext('{attr_type}({attr_value}) is not a valid type for {attr_name} in timeBase={time_base}')
ERR_SEMANTIC_VALIDATION_MISSING_ATTRIBUTES = gettext('{elem_name} is missing attributes: {attr_names}')
ERR_SEMANTIC_VALIDATION_INVALID_ATTRIBUTES = gettext('{elem_name} has invalid attributes: {attr_names}')
ERR_SEMANTIC_STYLE_MISSING = gettext('Style: {style} is not found.')
ERR_SEMANTIC_STYLE_CIRCLE = gettext('Style: {style} is in a circular reference.')
ERR_SEMANTIC_VALIDATION_EXPECTED = gettext('Please run semantic validation before calling this function')
ERR_SEMANTIC_ELEMENT_BY_ID_MISSING = gettext('Element with XML ID {id} is not found')
ERR_SEMANTIC_REGION_MISSING = gettext('Region: {region} is not found.')
ERR_SEMANTIC_ID_UNIQUENESS = gettext('XML ID is not unique: {id}')
ERR_DOCUMENT_NOT_COMPATIBLE = gettext('Document is not compatible with the sequence. Conflicting attributes: {attr_names}')
ERR_DOCUMENT_NOT_PART_OF_SEQUENCE = gettext('Document is not part of any sequence')
ERR_SEQUENCE_FROM_DOCUMENT = gettext('Sequence cannot be created from: {document}, EBUTT3Document instance expected!')
ERR_DOCUMENT_SEQUENCE_INCONSISTENCY = gettext('Timeline consistency problem.')
ERR_DOCUMENT_EXTENT_MISSING = gettext('{type} cannot be instantiated from {value} because document extent is missing (from the tt element)')
ERR_1DIM_ONLY = gettext('{type} accepts 1 dimensional values only')
ERR_2DIM_ONLY = gettext('{type} accepts 2 dimensional values only')
END_OF_DATA = gettext('End of available data reached')
ERR_UNKNOWN_HASH = gettext('The hash for this document is not known')

ERR_WS_INVALID_ACTION = gettext('Invalid action: {action}')
ERR_WS_NOT_PRODUCER = gettext('This socket does not belong to a producer.')
ERR_WS_NOT_CONSUMER = gettext('This socket does not belong to a consumer')
ERR_WS_SEND_VIA_CONSUMER = gettext('Consumer socket cannot be used to send data')
ERR_WS_RECEIVE_VIA_PRODUCER = gettext('Producer socket cannot be used to receive data')

ERR_CONF_ONE_BACKEND_ONLY = gettext('There is only one backend allowed. Already created: {backend1}, New: {backend2}')
ERR_CONF_NO_SUCH_NODE = gettext('No such node type found: {node_type}')
ERR_CONF_PROXY_CONF_VALUE = gettext('Failed to parse proxy config: {value}')
ERR_CONF_WS_SERVER_PROTOCOL_MISMATCH = gettext('The address: {address} is in use by another server with different protocol version')

DOC_SYNTACTIC_VALIDATION_SUCCESSFUL = gettext('Syntactic validation successful')
DOC_SEMANTIC_VALIDATION_SUCCESSFUL = gettext('Document {sequence_identifier}__{sequence_number} semantic validation successful')
DOC_PRODUCED = gettext('Document {sequence_identifier}__{sequence_number} produced')
DOC_DISCARDED = gettext('Document {sequence_identifier}__{sequence_number} is discarded')
DOC_INSERTED = gettext('Document {sequence_identifier}__{sequence_number} inserted into sequence')
DOC_TRIMMED = gettext('Document {sequence_identifier}__{sequence_number} activation change: [{resolved_begin_time}; {resolved_end_time}]')
DOC_RECEIVED = gettext('Document {sequence_identifier}__{sequence_number} received. Calculated activation: [{computed_begin_time}; {computed_end_time}]')
DOC_REQ_SEGMENT = gettext('{sequence_identifier}__{sequence_number}: requesting segment ({begin} - {end})')
DOC_SEQ_REQ_SEGMENT = gettext('{sequence_identifier}: requesting segment ({begin} - {end})')
