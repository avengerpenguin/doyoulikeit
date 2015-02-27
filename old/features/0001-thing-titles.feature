Feature: Thing titles

Scenario: Thing has a title
  When I visit the page for "Kevin Bacon"
  Then the page should have the title "Kevin Bacon"
