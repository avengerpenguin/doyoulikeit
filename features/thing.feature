Feature: Browsing things

Scenario: Thing has a title
  When I GET "/things/Postman_Pat"
  Then the response "title" should be "Postman Pat"

Scenario: Thing has a description
  When I GET "/things/Muscadet"
  Then the response "description" should be over 50 characters in length
