---
title: "ws-camerad"
note_category: "Raspberry Pi"
---

# ws-camerad

[ws-camerad](https://github.com/Wildlife-Systems/ws-camerad) is a camera daemon for Raspberry Pi that captures frames from CSI or USB cameras and distributes them to multiple consumers. It is part of the [Wildlife Systems](https://wildlife.systems) suite of tools for sensor networks.

## Relevant blog posts

{% assign tag_name = "ws-camerad" %}
{% if site.tags[tag_name] %}
<ul>
{% for post in site.tags[tag_name] %}
  <li><a href="{{ post.url }}">{{ post.title }}</a> <small>({{ post.date | date: "%Y-%m-%d" }})</small></li>
{% endfor %}
</ul>
{% endif %}
