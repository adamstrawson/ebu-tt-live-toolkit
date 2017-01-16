@buffer @delay
Feature: BufferDelayNode

  Examples:
  | xml_file      |
  | delayNode.xml |  

  # SPEC-CONFORMANCE.md R109, R112
  # Any delay introduced by the carriage mechanism can not lead to a test passing falsely. 
  # For example, if the desired delay offset is 10s and the carriage mech imposes a delay of 3s, 
  # then an actual delay in the range 7s -> 10s would lead to the test passing because the 3s of 
  # carriage delay would be added. This would not be correct.
  # BufferDelay.emission_time - BufferDelay.availability_time >= delay_offset

  Scenario: BufferDelayNode delays emission by no less than the delay period
    Given an xml file <xml_file>
    And the document is generated
    And it has availability time <avail_time>
    And the buffer delay node delays it by <delay_offset>
    And the document is emitted at <emission>
    Then the delta between <emission> and <avail_time> is greater or equal to <delay_offset>

    Examples:
    | emission   | avail_time  | delay_offset |
    | 00:00:05.0 | 00:00:02.0  | 00:00:01.0   |
