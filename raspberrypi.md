# Raspberry Pi

## Power management on Raspberry Pi

[pi-pwr](https://github.com/Wildlife-Systems/pi-pwr): Command line tool for managing power consumption on Raspberry Pi.

## General abstraction

[pi-data](https://github.com/Wildlife-Systems/pi-data): General abstraction layer for Raspberry Pi data

## Install and control sound devices

[sound-device-control](https://github.com/Wildlife-Systems/sound-device-control): Install and control sound devices on Raspberry Pi.

## Camera daemon

[ws-camerad](/notes/ws-camerad): Camera daemon for Raspberry Pi with frame rotation and virtual camera output via v4l2loopback.

## Install and control sensors

[sensor-control](https://github.com/Wildlife-Systems/sensor-control): Install and control sensors on the Raspberry Pi using a standard interface.

## Managing Raspberry Pi sensor networks

[Useful tools for maintaining Raspberry Pi sensor networks](/notes/raspberry-pi-tools): A list of tools and equipment that are useful for maintaining Raspberry Pi sensor networks.

## Relevant blog posts

{% assign tag_name = "Raspberry Pi" %}
{% if site.tags[tag_name] %}
<ul>
{% for post in site.tags[tag_name] %}
  <li><a href="{{ post.url }}">{{ post.title }}</a> <small>({{ post.date | date: "%Y-%m-%d" }})</small></li>
{% endfor %}
</ul>
{% endif %}
