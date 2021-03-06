Scripts and their functions
===========================

Simple Producer
---------------
This is a command line script. It loads static text from a file (``ebu-tt-live-toolkit/ebu_tt_live/examples/simple_producer.txt``) and breaks it into a sequence of EBU-TT Live documents using natural language processing. Run it by entering the command ``ebu-simple-producer`` without any arguments.

The default carriage mechanism is WebSocket, so you will need to listen to ``ws://127.0.0.1:9000``. Conveniently, we've created an HTML page that does just that. After you launch ``ebu-simple-producer``, open ``test.html`` in your browser. The 'Broadcast message' field should be populated with the correct address (``ws://localhost:9000``). Click 'Connect' and then 'Subscribe'. You can also change the identifier for the sequence. The documents should appear in the window below.

Alternatively, the Simple Producer can use the file system as the carriage mechanism. Start it with the folder argument, like this: ``ebu-simple-producer --folder-export myFolder``. This saves the documents in ``myFolder`` together with a manifest file that can be used by the Simple Consumer (below). See `<filesystem_carriage_mechanism.html>`__ for more details about the file system carriage mechanism.

Simple consumer
---------------
This script reads and validates documents in a sequence. It performs both semantic and syntactic validation of the XML. By default, it uses WebSocket and listens to ``ws://localhost:9000``, but you can also point it to the file system. If you saved the documents in a folder (using the folder export argument of the Simple Producer), you can start it with the location of the manifest file, like so: ``ebu-simple-consumer --manifest-path myFolder/manifest_sequence_identifier.txt``.

User Input Producer
-------------------
This is a web page that adds a user interface and various configurations to the Simple Producer. It needs to connect to either the User Input Consumer or a User Input Forwarder. First, start ``ebu-user-input-consumer`` or ``ebu-user-input-forwarder`` from the command line. Then, in your browser, open ``ebu_tt_live/ui/user_input_producer/user_input_producer.html`` and click 'Connect'. Select the sending mode (manual, scheduled or asynchronous). You should see the documents arriving in the command line window where ``ebu-user-input-consumer`` is listening. See detailed instructions here: `<user_input_producer.html>`__.


User Input Consumer
-------------------
This is very similar to the Simple Consumer. It also performs validation but it does not have a manifest option. It provides a WebSocket connection point for the User Input Producer. You'll need to start either this or the User Input Forwarder before connecting the User Input Producer (but not both).

User Input Forwarder
--------------------
This script mimics a distribution node. It listens to documents coming from the User Input Producer on ``ws://127.0.0.1:9001`` and forwards them to any consumer listening on ``ws://127.0.0.1:9000``. Like the Simple Producer, it can also save the documents it receives to the file system. First, run it with the ``--folder-export`` argument like this: ``ebu-user-input-forwarder --folder-export myFolder``. Then launch the User Input Producer and connect. The sequence will be saved to ``myFolder`` along with the manifest file. The User Input Forwarder can also be used as an incoming connection point for WebSocket connections from sources other than the User Input Producer.

EBU-TT-D Encoder
----------------
This script is an extension of simple consumer and is responsible for resegmenting and converting the incoming
EBU-TT Live documents into EBU-TT-D documents that can be later used to be embedded in video streams such as DASH.
The script launches with the ``ebu-ebuttd-encoder`` command. There are switches to control the mediatime conversion
reference point and the segmentation interval. Please run ``ebu-ebuttd-encoder --help`` to find our more.

The ebu-run script
------------------
This script is capable of picking up a structured configuration file and use that to create the nodes and carriage mechanism objects that we would like to use and they can be even wired in the same configuration file together so in the end a complex system can be modeled using a single json file. Please refer to :py:mod:`ebu_tt_live.scripts.ebu_run` as well as :py:mod:`ebu_tt_live.config` to learn more about the way the configuration logic works. To get help on permitted options for the specified node(s) run ``ebu-run`` with a ``--help``. See :doc:`configurator`.
