module Jekyll
  class HtmlRedirectGenerator < Generator
    safe true
    priority :lowest

    def generate(site)
      pages_to_redirect = site.posts.docs + site.pages

      pages_to_redirect.each do |page|
        url = page.url

        # If the page already ends with .html, skip
        next if url.end_with?('.html')
        # Skip pages with no meaningful path
        next if url == '/'

        html_url = "#{url}.html"

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
