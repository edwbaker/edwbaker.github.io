---
layout: default
title: Tags
description: All blog post tags
---

# Tags

{% assign sorted_tags = site.tags | sort %}
{% for tag in sorted_tags %}
<h2 id="{{ tag[0] | slugify }}">{{ tag[0] }} ({{ tag[1].size }})</h2>
<ul>
  {% for post in tag[1] %}
  <li><a href="{{ post.url }}">{{ post.title }}</a> <small>({{ post.date | date: "%Y-%m-%d" }})</small></li>
  {% endfor %}
</ul>
{% endfor %}
