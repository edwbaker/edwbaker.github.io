---
layout: default
title: Notes
description: Notes and resources by Ed Baker
---

# Notes

{% assign notes_pages = site.pages | where_exp: "p", "p.note_category" | sort: "note_category" %}
{% assign notes_by_category = notes_pages | group_by: "note_category" %}
{% for category in notes_by_category %}
## {{ category.name }}
{: id="{{ category.name | slugify }}"}

{% assign has_subcategories = category.items | where_exp: "item", "item.note_subcategory" | size %}
{% if has_subcategories > 0 %}
{% assign subcats = category.items | group_by: "note_subcategory" %}
{% for subcat in subcats %}
{% if subcat.name and subcat.name != "" %}
### {{ subcat.name }}

{% endif %}
{% for note in subcat.items %}
- [{{ note.title }}]({{ note.url }})

{% endfor %}
{% endfor %}
{% else %}
{% for note in category.items %}
- [{{ note.title }}]({{ note.url }})

{% endfor %}
{% endif %}
{% endfor %}
