module Jekyll
  class HtmlRedirectGenerator < Generator
    safe true
    priority :lowest

    def generate(site)
      site.posts.docs.each do |post|
        url = post.url

        next if url.end_with?('.html')
        next if url == '/'

        html_url = "#{url}.html"

        # Skip if the post's own destination already lives at this .html path.
        # Jekyll writes posts to <url>.html (or <url>/index.html) so creating
        # a redirect page at the same path causes a conflict warning.
        dest = post.destination(site.dest)
        next if dest.end_with?("#{url}.html") || dest.end_with?("#{url}/index.html")

        site.pages << RedirectPage.new(site, site.source, html_url, url)
      end
    end
  end

  class RedirectPage < Page
    def initialize(site, base, redirect_from, redirect_to)
      @site = site
      @base = base
      @dir  = File.dirname(redirect_from)
      @name = File.basename(redirect_from)

      self.process(@name)
      self.data = {
        'layout' => nil,
        'sitemap' => false,
      }
      self.content = <<~HTML
        <!DOCTYPE html>
        <html lang="en">
        <head>
          <meta charset="utf-8">
          <link rel="canonical" href="#{redirect_to}">
          <meta http-equiv="refresh" content="0; url=#{redirect_to}">
        </head>
        <body>
          <p>Redirecting to <a href="#{redirect_to}">#{redirect_to}</a>...</p>
        </body>
        </html>
      HTML
    end
  end
end
