Configuration files and ``ebu-run``
===================================

There are 2 ways the nodes and carriage mechanisms can be set up:

    1. Write a script where you instantiate these components and connect them. This technique uses
    dependency injection. This means the nodes and carriage mechanisms do not need to know about the creation of
    each other. They just get the already created component referenced as a parameter, and check if that component
    implements the expected interface. This eliminates the possibility of creating spaghetti code where every node would know
    how to create every carriage mechanism and deal with all the possible parameters and every carriage mechanism would know
    in turn how to instantiate every node. This is to be avoided! And this brings us to the second way to do this.

    2. Use the component configurators and use a simple configuration file to create your system and give the
    configuration file to the :py:mod:`ebu_tt_live.scripts.ebu_run` script, which takes care of creating all the
    required components for you. This eliminates the need for a programmer to keep repeating the configuration logic
    in their scripts where they create the components.

The idea is the following: The components(nodes, carriage mechanisms, converters, re-sequencers...etc.) are agnostic
to one another as long as the carriage mechanism is capable of transporting the payload the node expects. But their
wiring and their factories are actually the configurator classes. The configurator class defines the type and
name of the configuration options relevant to the component and wires it with its immediate dependencies. This
way the factories that create the system are separate from the system's business logic and this separation is
meant to be kept. There is a simple naming correspondence. For instance the business logic of the processing
nodes are in the :py:mod:`ebu_tt_live.node` package while their configurators are to be found in the
:py:mod:`ebu_tt_live.config.node` module.

The configuration file structure
--------------------------------

The configuration file is JSON at the moment. The general structure looks like this:

    ::

        {
            "nodes": {
                "node1": {
                    "type": "simple-producer",
                    "output": { ... }
                    ...
                },
                "node2": { ... },
                ...
            },
            "backend": {
                "type": "twisted",
                ...
            }
        }

The nodes are supposed to be compatible with the chosen backend. The backend object is instantiated first and
every component configurator has access to the backend that was created and it is their responsibility to
ensure that compatibility is checked with the backend. The backend provides a framework for
timing things, network stack access, threading... etc. Different backends may offer different features and if
a component configurator is not compatible with the backend object it should raise a ConfigurationError.

The node contains either an input or an output section or both in case it is a node that both receives and emits
sequences at the same time, like a forwarder node, a handover node, a converter... etc. The input and output bits
define the carriage mechanism that that side is supposed to be talking to. So providing 2 nodes: 1) a producer with
an output carriage mechanism that is "websocket" and 2) a consumer of an input carriage mechanism of the same websocket
address that the producer is using essentially creates a loopback through the network stack between the 2 nodes
and they will talk to one another. An even more convenient way of doing the same thing is to use
the carriage mechanism type: ``direct`` which simply transfers the payload data in memory without going via e.g. a network stack.

The more detailed options are: ::

    nodes
    ├─[nodeN] : a node to configure - any from node1 to node9
    │ ├─type : ["simple-consumer" | "simple-producer" | "resequencer" | "ebuttd-encoder" | "buffer-delay" | "retiming-delay" | "distributor"]
    │ ├─output : the output settings for the node, if applicable
    │ │ ├─carriage : the carriage mechanism to use to get incoming documents
    │ │ │ ├─type : ["direct" | "filesystem" | "filesystem-simple" | "websocket" | "websocket-legacy"]
    │ │ │ └─[output carriage type-dependent options - see below]
    │ │ └─adapters : see below
    │ ├─input : the input settings for the node, if applicable
    │ │ ├─carriage : the carriage mechanism to use to emit outgoing documents
    │ │ │ ├─type : ["direct" | "filesystem" | "websocket" (default) | "websocket-legacy"]
    │ │ │ └─[input carriage type-dependent options - see below]
    │ │ └─adapters : see below
    │ ├─id : identifier for the node, defaults to a value based on the node's type.
    │ └─[node type-dependent options - see below]
    backend
    └─type: ["twisted" (default) | "dummy"]    

Node type dependent options for [nodeN] : ::

   type="simple-consumer"
   ├─verbose : whether to log subtitle content on activation changes, default False
   └─clock
     └─type : ["auto" (default) | "utc" | "local"]

   type="simple-producer"
   ├─show_time : Whether to put the current time in the output text (true) or use the default text file input (false, default)
   ├─sequence_identifier : sequence identifier, default "TestSequence1"
   ├─interval : period between each document in seconds, default 2
   └─clock
     └─type : ["local" (default) | "auto" | "clock"]

   type="resequencer"
   ├─sequence_identifier : sequence identifier, default "re-sequencer"
   ├─segment_length : duration of each output segment in seconds, default 2
   ├─begin_output : ["immediate" (default) | {begin time} ] the time at which the first output segment should begin.
   ├─discard : whether to discard content that has been encoded, default True
   └─clock
     └─type : ["local" (default) | "auto" | "clock"]

   type="ebuttd-encoder"
   ├─media_time_zero : ["current" (default) | clock time at media time zero TODO: check format]
   ├─default_namespace : ["false" (default) | "true"]
   └─clock
     └─type : ["local" (default) | "auto" | "utc"]

   type="buffer-delay"
   └─delay : delay in seconds, default 0

   type="retiming-delay"
   ├─delay : delay in seconds, default 0
   └─sequence_identifier : sequence identifier, default "RetimedSequence1"

   type="distributor" : No options

Output carriage type dependent options for "carriage": ::

   type="direct"
   └─id : id of the 'pipe' to write to, default "default"

   type="filesystem"
   └─folder : The output folder/directory. Folder is created if it does not exist. Existing files are overwritten, default "./export"

   type="filesystem-simple"
   ├─folder : The output folder/directory. Folder is created if it does not exist. Existing files are overwritten, default "./export"
   ├─rotating_buf : Rotating buffer size. This will keep the last N number of files created in the folder., default 0
   └─filename_pattern : File name pattern. It needs to contain {counter} format parameter, default "export-{counter}.xml"

   type="websocket"
   ├─proxy : HTTP proxy in format ADDR:PORT
   ├─listen : Socket to listen on for /subscribe connection requests i.e: ws://ADDR:PORT, default "ws://localhost:9001"
   └─connect : List of /publish connections to make. Expected values are URL strings which will be parsed; if one does not conform to the pattern a config error will be generated..
     └─Example: ws://<host>:<port>/<sequenceIdentifier>/publish

   type="websocket-legacy"
   └─uri : URI to listen for connections on, default "ws://localhost:9001"

Input carriage type dependent options for "carriage": ::

   type="direct"
   └─id : id of the pipe to read from, default "default"

   type="filesystem"
   ├─manifest_file : The timing manifest file for importing files. Files are required to be in the same folder as the manifest file.
   └─tail : Keep the manifest open and wait for new input much like UNIX's tail -f command

   type="filesystem-simple"
   ├─folder : The output folder/directory. Folder is created if it does not exist. Existing files are overwritten, default "./export"
   ├─rotating_buf : Rotating buffer size. This will keep the last N number of files created in the folder., default 0
   └─filename_pattern : File name pattern. It needs to contain {counter} format parameter, default "export-{counter}.xml"

   type="websocket"
   ├─proxy : HTTP proxy in format ADDR:PORT
   ├─listen : Socket to listen on for /publish connection requests i.e: ws://ADDR:PORT, default "ws://localhost:9001"
   └─connect : List of /subscribe connections to make. Expected values are URL strings which will be parsed; if one does not conform to the pattern a config error will be generated..
     └─Example: ws://<host>:<port>/<sequenceIdentifier>/subscribe

   type="websocket-legacy"
   ├─proxy : HTTP proxy in format ADDR:PORT
   └─uri : URI to connect to, default "ws://localhost:9001"

Adapters will be automatically selected if not specified, or can be manually specified: ::

    adapters
    ├─xml->ebutt3 : XML serialisation to EBU-TT Part 3
    ├─xml->ebuttd : XML serialisation to EBU-TT-D
    ├─ebutt3->xml : EBU-TT Part 3 to XML serialisation
    └─ebuttd->xml : EBU-TT-D to XML serialisation

Please refer to the :py:mod:`ebu_tt_live.scripts.ebu_run` for more information. Example ``.conf`` files for some common configurations can be found in ``examples/config``  
