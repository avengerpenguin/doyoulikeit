Feature: Thing titles

Scenario: Thing has a title
  When I visit the page for Kevin Bacon
  Then the page should have the title "Kevin Bacon"

#Scenario: Thing has a description
#  When I GET "/things/Muscadet"
#  Then the response "description" should be over 50 characters in length
