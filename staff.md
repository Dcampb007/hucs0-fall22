---
layout: page
title: Staff
description: A listing of all the course staff members.
---

# Staff

For a quicker response on homework or project help, please ask on Piazza rather than emailing staff members individually. On Piazza, all staff members can see your question and answer it.

## Instructors

{% assign instructors = site.staffers | where: 'role', 'Instructor' %}
{% for staffer in instructors %}
{{ staffer }}
{% endfor %}

{% assign howard_teaching_assistants = site.staffers | where: 'role', 'Howard Teaching Assistant' %}
{% assign num_howard_teaching_assistants = howard_teaching_assistants | size %}
{% if num_howard_teaching_assistants != 0 %}
## Howard Teaching Assistants

{% for staffer in howard_teaching_assistants %}
{{ staffer }}
{% endfor %}
{% endif %}

{% assign google_teaching_assistants = site.staffers | where: 'role', 'Google Teaching Assistant' %}
{% assign num_google_teaching_assistants = google_teaching_assistants | size %}
{% if num_google_teaching_assistants != 0 %}
## Google Teaching Assistants

{% for staffer in google_teaching_assistants %}
{{ staffer }}
{% endfor %}
{% endif %}

{% assign google_career_coaches = site.staffers | where: 'role', 'Google Career Coach' %}
{% assign num_google_career_coaches = google_career_coaches | size %}
{% if num_google_career_coaches != 0 %}
## Google Career Coaches

{% for staffer in google_career_coaches %}
{{ staffer }}
{% endfor %}
{% endif %}
