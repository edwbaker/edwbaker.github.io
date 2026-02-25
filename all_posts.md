# All blog posts

<div id="pagination-controls-top" class="pagination-controls"></div>

<ul id="post-list">
  {% for post in site.posts %}
    <li class="post-item" data-year="{{ post.date | date: '%Y' }}">
      <span class="post-date">{{ post.date | date: "%Y-%m-%d" }}</span> &mdash;
      <a href="{{ post.url }}">{{ post.title }}</a>
    </li>
  {% endfor %}
</ul>

<div id="pagination-controls-bottom" class="pagination-controls"></div>

<style>
  .post-item { display: none; }
  .post-item.visible { display: list-item; }
  .post-date { color: #888; font-size: 0.9em; font-family: monospace; }
  .pagination-controls {
    display: flex;
    align-items: center;
    gap: 8px;
    flex-wrap: wrap;
    margin: 1em 0;
  }
  .pagination-controls button {
    padding: 4px 12px;
    cursor: pointer;
    border: 1px solid #ccc;
    background: #f5f5f5;
    border-radius: 3px;
  }
  .pagination-controls button:hover:not(:disabled) {
    background: #ddd;
  }
  .pagination-controls button:disabled {
    opacity: 0.4;
    cursor: default;
  }
  .pagination-controls .page-info {
    margin: 0 8px;
    font-size: 0.9em;
  }
  .pagination-controls select {
    padding: 4px;
    border: 1px solid #ccc;
    border-radius: 3px;
  }
</style>

<script>
(function() {
  var perPage = 20;
  var items = document.querySelectorAll('.post-item');
  var total = items.length;
  var totalPages = Math.ceil(total / perPage);
  var currentPage = 1;

  // Check URL hash for page number
  var hash = window.location.hash.match(/^#page(\d+)$/);
  if (hash) {
    var p = parseInt(hash[1], 10);
    if (p >= 1 && p <= totalPages) currentPage = p;
  }

  function showPage(page) {
    currentPage = page;
    var start = (page - 1) * perPage;
    var end = start + perPage;
    for (var i = 0; i < total; i++) {
      items[i].classList.toggle('visible', i >= start && i < end);
    }
    window.location.hash = 'page' + page;
    renderControls();
    window.scrollTo(0, 0);
  }

  function renderControls() {
    ['top', 'bottom'].forEach(function(pos) {
      var el = document.getElementById('pagination-controls-' + pos);
      el.innerHTML = '';

      var first = document.createElement('button');
      first.textContent = '« First';
      first.disabled = currentPage === 1;
      first.onclick = function() { showPage(1); };
      el.appendChild(first);

      var prev = document.createElement('button');
      prev.textContent = '‹ Prev';
      prev.disabled = currentPage === 1;
      prev.onclick = function() { showPage(currentPage - 1); };
      el.appendChild(prev);

      var info = document.createElement('span');
      info.className = 'page-info';
      info.textContent = 'Page ' + currentPage + ' of ' + totalPages + ' (' + total + ' posts)';
      el.appendChild(info);

      var next = document.createElement('button');
      next.textContent = 'Next ›';
      next.disabled = currentPage === totalPages;
      next.onclick = function() { showPage(currentPage + 1); };
      el.appendChild(next);

      var last = document.createElement('button');
      last.textContent = 'Last »';
      last.disabled = currentPage === totalPages;
      last.onclick = function() { showPage(totalPages); };
      el.appendChild(last);

      // Year jump selector
      var years = [];
      for (var i = 0; i < total; i++) {
        var y = items[i].getAttribute('data-year');
        if (years.indexOf(y) === -1) years.push(y);
      }
      var sel = document.createElement('select');
      var defOpt = document.createElement('option');
      defOpt.textContent = 'Jump to year…';
      defOpt.value = '';
      sel.appendChild(defOpt);
      years.forEach(function(y) {
        var opt = document.createElement('option');
        opt.value = y;
        opt.textContent = y;
        sel.appendChild(opt);
      });
      sel.onchange = function() {
        if (!this.value) return;
        for (var i = 0; i < total; i++) {
          if (items[i].getAttribute('data-year') === this.value) {
            showPage(Math.floor(i / perPage) + 1);
            this.value = '';
            return;
          }
        }
      };
      el.appendChild(sel);
    });
  }

  showPage(currentPage);
})();
</script>
