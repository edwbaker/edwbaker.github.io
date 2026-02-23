module Jekyll
  class VideoSitemapGenerator < Generator
    safe true
    priority :low

    def generate(site)
      video_pages = site.pages.select { |p| p.data['video'] }
      return if video_pages.empty?

      site.pages << VideoSitemapPage.new(site, video_pages)
    end
  end

  class VideoSitemapPage < Page
    def initialize(site, video_pages)
      @site = site
      @base = site.source
      @dir  = ''
      @name = 'video-sitemap.xml'

      self.process(@name)
      self.data = {
        'layout' => nil,
        'sitemap' => false,
      }

      base_url = site.config['url'] || ''

      xml = []
      xml << '<?xml version="1.0" encoding="UTF-8"?>'
      xml << '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"'
      xml << '        xmlns:video="http://www.google.com/schemas/sitemap-video/1.1">'

      video_pages.each do |page|
        video = page.data['video']
        page_url = "#{base_url}#{page.url}"
        content_url = "#{base_url}#{video['src']}"
        thumbnail_url = "#{base_url}#{video['thumbnail']}"
        title = page.data['title'] || ''
        description = page.data['description'] || title
        upload_date = (page.data['date'] || site.time).strftime('%Y-%m-%d')

        xml << '  <url>'
        xml << "    <loc>#{escape(page_url)}</loc>"
        xml << '    <video:video>'
        xml << "      <video:content_loc>#{escape(content_url)}</video:content_loc>"
        xml << "      <video:thumbnail_loc>#{escape(thumbnail_url)}</video:thumbnail_loc>"
        xml << "      <video:title>#{escape_text(title)}</video:title>"
        xml << "      <video:description>#{escape_text(description)}</video:description>"
        xml << "      <video:publication_date>#{upload_date}</video:publication_date>"
        if video['duration']
          xml << "      <video:duration>#{video['duration']}</video:duration>"
        end
        xml << '    </video:video>'
        xml << '  </url>'
      end

      xml << '</urlset>'

      self.content = xml.join("\n")
    end

    private

    def escape(str)
      str.to_s
        .gsub('&', '&amp;')
        .gsub('<', '&lt;')
        .gsub('>', '&gt;')
        .gsub("'", '&apos;')
        .gsub('"', '&quot;')
    end

    def escape_text(str)
      escape(str)
    end
  end
end
