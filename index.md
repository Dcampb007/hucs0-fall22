---
layout: home
title: Home
nav_exclude: true
seo:
  type: Course
  name: CS0 Howard
---

# {{ site.tagline }}
{: .mb-2 }
{{ site.description }}
{: .fs-6 .fw-300 }



## Welcome to your course homepage
This page will display the most recent announcement AND course outline. You can find the complete list of announcements and course modules in the navigation bar. 

## About the Class

CSCI100 (aka CS0) is an introductory class designed for students with no formal exposure to computer science or programming. The goal is to provide a gentle but thorough introduction to computer science that will prepare students to either take further computer science courses, or use computer science in their field of study.

See the [Syllabus page](syllabus.md) for more details on course policies.

## Announcements
{% if site.announcements %}
{{ site.announcements.last }}
[All Announcements](announcements.md){: .btn}
{% endif %}

## Course Modules
{% if site.modules %}
{{ site.modules.last }}
[All Course Modules](course_outline.md){: .btn}
{% endif %}
