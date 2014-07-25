Feature: Short descriptions of things appear on their pages

Scenario: Errol Brown has a description on his page
  When I visit the page for Errol Brown
  Then the page should have some kind of description of him
