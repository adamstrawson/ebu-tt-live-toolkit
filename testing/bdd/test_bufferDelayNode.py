from pytest_bdd import scenarios, given, when, then


scenarios('features/timing/bufferDelayNode.feature')


# functions for scenario: BufferDelayNode delays emission by no less than the delay period

@given('the buffer delay node delays it by <delay_offset>')
def given_buffer_delay():
    pass


@given('the document is emitted at <emission>')
def given_document_emitted():
    pass


@then('the delta between <emission> and <avail_time> is greater or equal to <delay_offset>')
def then_delta_should_be_correct(emission, avail_time, delay_offset):

    # BufferDelay.emission_time - BufferDelay.availability_time >= delay_offset
    pass


# functions for scenario: BufferDelayNode does not modify the document

@given('the document has original hashed value <hash_1>')
def given_original_hash_value(hash_1):
    pass


@then('the document has new hashed value <hash_2>')
def then_original_hash_value(hash_2):
    pass
