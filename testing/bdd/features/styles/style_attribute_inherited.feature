@styles @document @inherited
Feature: Compute style attribute on a single EBU-TT Live element

  Examples:
  | xml_file                      | cell_resolution | extent      |
  | style_attribute_inherited.xml | 32 15           | 320px 150px |


  # Inheritence: region (S1) > div (S2) > p (S3) > span (S4)
  Scenario: Font size inheritance
    Given an xml file <xml_file>
    When it has a cell resolution of <cell_resolution>
    And it has extent of <extent>
    And it contains style S1 with <style_attribute> value <S1_value>
    And it contains style S2 with <style_attribute> value <S2_value>
    And it contains style S3 with <style_attribute> value <S3_value>
    And it contains style S4 with <style_attribute> value <S4_value>
    And the document is generated
    Then the computed <style_attribute> in <elem_id> is <computed_value>

    Examples:
    | S1_value  | S2_value | S3_value       | S4_value | style_attribute      | elem_id | computed_value |
    |           |          |                |          | tts:direction        | span1   | ltr            |
    | rtl       |          |                |          | tts:direction        | span1   | rtl            |
    | white     | blue     |                |          | tts:color            | span1   | blue           |
    |           |          |                |          | tts:color            | span1   |                |
    |           | serif    | monospaceSerif |          | tts:fontFamily       | span1   | monospaceSerif |
    |           |          |                |          | tts:fontFamily       | span1   | default        |
    |           | normal   | italic         |          | tts:fontStyle        | span1   | italic         |
    |           |          |                |          | tts:fontStyle        | span1   | normal         |
    |           | bold     | normal         | bold     | tts:fontWeight       | span1   | bold           |
    |           |          |                |          | tts:fontWeight       | span1   | normal         |
    | 0.5c      | 0c       | 0.5c           |          | ebutts:linePadding   | span1   | 0.5c           |
    |           |          |                |          | ebutts:linePadding   | span1   | 0c             |
    | center    |          | end            |          | ebutts:multiRowAlign | p1      | end            |
    |           |          |                |          | ebutts:multiRowAlign | p1      | auto           |
    | center    | start    | center         |          | tts:textAlign        | p1      | center         |
    |           |          |                |          | tts:textAlign        | p1      | start          |
    | underline | none     | underline      |          | tts:textDecoration   | span1   | underline      |
    |           |          |                |          | tts:textDecoration   | span1   | none           |
    | noWrap    | wrap     | noWrap         | wrap     | tts:wrapOption       | span1   | wrap           |
    |           |          |                |          | tts:wrapOption       | span1   | wrap           |


# default_value |
# ltr           |
#               |
# default       |
# normal        |
# normal        |
# 0c            |
# auto          |
# start         |
# none          |
# wrap          |

# fontStyle=oblique not allowed?