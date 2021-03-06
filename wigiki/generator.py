import os
from jinja2 import Environment, FileSystemLoader
from wigiki.builder import Builder

class SiteGenerator(object):
    def __init__(self, template_dir, output_dir, base_url, gists, site):
        loader = FileSystemLoader(template_dir)
        self.env = Environment(loader=loader)
        self.output_dir = output_dir
        self.gists = gists
        self.site = site

        if base_url == '/':
            self.base_url = base_url
        else:
            self.base_url = "/{}/".format(base_url.strip('/'))

    def _render(self, template, data):
        tpl = self.env.get_template(template)
        return tpl.render(data)


    def _parse_gists(self):
        gists = {}
        pages = []

        for username, gist_dict in self.gists.items():
            for title, gist_id in gist_dict.items():
                user_gid = "/".join((username, gist_id))
                gists[title] = Builder.gist(user_gid)
                pages.append(title)

        return gists, sorted(pages)


    def _save_file(self, filename, contents):
        """write the html file contents to disk"""
        with open(filename, 'w') as f:
            f.write(contents)


    def run(self):
        # parse data
        gists, pages = self._parse_gists()

        # index page
        try:
            os.mkdir(self.output_dir)
        except OSError as e:
            pass

        # template data for main index.html file
        tpl_data = {}
        tpl_data['site'] = self.site
        # use html pages
        tpl_data['pages'] = Builder.page_list(pages, self.base_url)
        tpl_data['gists'] = gists

        index_contents = self._render("base.html", tpl_data)
        index_file = os.path.join(self.output_dir, "index.html")
        self._save_file(index_file, index_contents)

        for title in pages:
            try:
                page_dir = os.path.join(self.output_dir, Builder.slugify(title))
                os.mkdir(page_dir)
            except OSError as e:
                pass

            tpl_data['gist'] = gists[title]
            tpl_data['title'] = title
            page_contents = self._render("page.html", tpl_data)
            page_file = os.path.join(page_dir, "index.html")
            self._save_file(page_file, page_contents)

