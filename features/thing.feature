Feature: Browsing things

Scenario: Thing has a title
  When I GET "/things/Postman_Pat"
  Then the response "title" should be "Postman Pat"
