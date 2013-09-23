Feature: Voting on things

Scenario: View popularity
  When I GET "/things/Yule"
  Then the response "popularity" should be a number

Scenario: Add like to a thing
  Given I am a new visitor
  When I POST to "/things/Gore_Vidal/like"
  Then the response should be status 303
  And the response should have "Location" header matching ".*/thing/Gore_Vidal"
