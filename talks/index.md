---
layout: default
title: Talks
description: Presentations and talks by Ed Baker
---

# Talks

{% assign talks_by_year = site.data.talks | group_by: "year" | sort: "name" | reverse %}
{% for year in talks_by_year %}
## {{ year.name }}

{% for talk in year.items %}
- {% if talk.url %}[{{ talk.date }} - {{ talk.title }}]({{ talk.url }}){% else %}{{ talk.date }} - {{ talk.title }}{% endif %}{% if talk.description %} - {{ talk.description }}{% endif %}

{% endfor %}
{% endfor %}
