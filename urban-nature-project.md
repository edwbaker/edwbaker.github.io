# Urban Nature Project

The Urban Nature Project is a major initiative at the Natural History Museum, London, aimed at transforming the Museum's gardens into an [Urban Research Station](/urban-research-station): a living laboratory for urban biodiversity research. The project focuses on understanding and enhancing urban ecosystems through innovative research, community engagement, and the use of technology.

- [Urban Nature Project](https://www.nhm.ac.uk/about-us/urban-nature-project.html) - official project page

## NHM gardens transformation

- [Pond transformation](/notes/urs-pond-transformation) - transformation of the NHM Wildlife Garden pond system into the new pond system in the Nature Discovery Garden.

## In the media

- [The Nature of Tech](https://aws.amazon.com/uki/cloud-services/sustainability-aws-and-nhm/) - Amazon Web Services and the Natural History Museum (2025) - discussing the use of technology in biodiversity research.

- [Natural History Museum's new gardens aim to restore UK's urban nature](https://www.newscientist.com/video/2440498-natural-history-museums-new-gardens-aim-to-restore-uks-urban-nature/) New Scientist (2024)

{% include youtube.html id="3CovYvcTnuw" start="0" title = "Inside one of the UK's most studied urban nature sites" %}

- ITV News (2024) Discussing audio sensor network in NHM Gardens.

![Ed Baker on ITV News](/imgs/unp-itv.png)

- [Urban Nature Project at the Natural History Museum review – it’s a wondrous jungle out there](https://www.theguardian.com/culture/article/2024/jul/21/urban-nature-project-natural-history-museum-london-new-gardens-fern-diplodocus) - The Guardian (2024) - a review of the Urban Nature Project at the Natural History Museum.

- [‘You travel five million years a metre’: inside the Natural History Museum’s mind-boggling new garden](https://www.theguardian.com/artanddesign/article/2024/jul/16/natural-history-museum-garden-fern-dippy) - The Guardian (2024)

## Miscellaneous Activities

- [List](/unp-activities) - a list of activities related to the Urban Nature Project.

## Relevant blog posts

{% assign tag_name = "urban nature project" %}
{% if site.tags[tag_name] %}
<ul>
{% for post in site.tags[tag_name] %}
  <li><a href="{{ post.url }}">{{ post.title }}</a> <small>({{ post.date | date: "%Y-%m-%d" }})</small></li>
{% endfor %}
</ul>
{% endif %}